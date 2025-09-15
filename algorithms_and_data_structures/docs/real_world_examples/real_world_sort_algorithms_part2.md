# Real-World Sort Algorithms: Part 2

## Financial Trading Order Book

### 💹 High-Frequency Trading Order Matching
**Purpose**: Sorts millions of orders per second for market matching
**Real Usage**: NYSE, NASDAQ, CME, Binance, Interactive Brokers

```pseudocode
╔════════════════════════════════════════════════════════════════════╗
║ ALGORITHM: Radix Sort for Order Books with Price-Time Priority    ║
║ Orders/sec: 10M+ | Latency: <1μs | Deterministic: Yes             ║
╚════════════════════════════════════════════════════════════════════╝

▶ INPUT PARAMETERS:
  orders: array[Order]               # Incoming orders
  order_book: OrderBook              # Current market state
  market_rules: TradingRules         # Price tick sizes, limits
  risk_limits: RiskParameters        # Position limits, margin
  
▶ OUTPUT:
  executions: array[Trade]           # Matched trades
  updated_book: OrderBook            # New order book state
  market_data: MarketUpdate          # Price/volume updates

▶ DATA STRUCTURES:
  Order: {
    id: uint64                      # Unique order ID
    timestamp: uint64               # Nanosecond precision
    side: enum {BUY, SELL}
    price: int64                    # Price in cents/ticks
    quantity: uint32                # Number of shares
    type: enum {MARKET, LIMIT, STOP}
    time_in_force: enum {DAY, GTC, IOC, FOK}
    account_id: uint32
  }
  
  OrderBook: {
    bids: array[PriceLevel]         # Buy orders (sorted high to low)
    asks: array[PriceLevel]         # Sell orders (sorted low to high)
    last_trade_price: int64
    total_volume: uint64
  }
  
  PriceLevel: {
    price: int64
    orders: Queue[Order]            # FIFO queue at this price
    total_quantity: uint32
  }

▶ ALGORITHM PHASE 1: Radix Sort for Price Levels
FUNCTION radixSortOrders(orders, max_price_digits=8):
    
    ══════ STEP 1: Separate by Side ══════
    buy_orders ← []
    sell_orders ← []
    
    FOR order IN orders:
        IF order.side == BUY:
            buy_orders.append(order)
        ELSE:
            sell_orders.append(order)
    
    ══════ STEP 2: Radix Sort by Price ══════
    # LSD Radix sort for positive integers
    FUNCTION radixSortByPrice(orders, descending=FALSE):
        IF length(orders) <= 1:
            RETURN orders
        
        # Find max price for digit count
        max_price ← MAX(order.price FOR order IN orders)
        num_digits ← numberOfDigits(max_price)
        
        # Use base 256 for byte-level efficiency
        RADIX ← 256
        
        FOR digit_pos FROM 0 TO num_digits-1:
            # Counting sort for current digit
            buckets ← [[] FOR i IN range(RADIX)]
            
            FOR order IN orders:
                # Extract digit at position
                digit ← (order.price >> (digit_pos × 8)) & 0xFF
                
                IF descending:
                    digit ← RADIX - 1 - digit
                
                buckets[digit].append(order)
            
            # Concatenate buckets
            orders ← []
            FOR bucket IN buckets:
                orders.extend(bucket)
        
        RETURN orders
    END FUNCTION
    
    # Sort buy orders descending (highest price first)
    sorted_buys ← radixSortByPrice(buy_orders, descending=TRUE)
    
    # Sort sell orders ascending (lowest price first)
    sorted_sells ← radixSortByPrice(sell_orders, descending=FALSE)
    
    RETURN sorted_buys, sorted_sells
END FUNCTION

▶ ALGORITHM PHASE 2: Time Priority Within Price Levels
FUNCTION maintainTimePriority(orders_at_price):
    
    ══════ Stable Sort by Timestamp ══════
    # Use counting sort for nanosecond timestamps
    
    IF length(orders_at_price) <= 1:
        RETURN orders_at_price
    
    # Normalize timestamps to relative values
    min_time ← MIN(order.timestamp FOR order IN orders_at_price)
    max_time ← MAX(order.timestamp FOR order IN orders_at_price)
    
    IF max_time == min_time:
        RETURN orders_at_price  # All same time
    
    # Bucket by timestamp ranges
    num_buckets ← MIN(length(orders_at_price), 1000)
    bucket_size ← (max_time - min_time + 1) / num_buckets
    buckets ← [[] FOR i IN range(num_buckets)]
    
    FOR order IN orders_at_price:
        bucket_idx ← MIN(
            FLOOR((order.timestamp - min_time) / bucket_size),
            num_buckets - 1
        )
        buckets[bucket_idx].append(order)
    
    # Concatenate maintaining order
    sorted_orders ← []
    FOR bucket IN buckets:
        sorted_orders.extend(bucket)
    
    RETURN sorted_orders
END FUNCTION

▶ ALGORITHM PHASE 3: Order Matching Engine
FUNCTION matchOrders(order_book, new_order):
    
    executions ← []
    
    ══════ Market Order Matching ══════
    IF new_order.type == MARKET:
        IF new_order.side == BUY:
            # Match against asks (sell orders)
            remaining_qty ← new_order.quantity
            
            WHILE remaining_qty > 0 AND NOT order_book.asks.isEmpty():
                best_ask_level ← order_book.asks[0]
                
                WHILE remaining_qty > 0 AND NOT best_ask_level.orders.isEmpty():
                    sell_order ← best_ask_level.orders.peek()
                    
                    # Determine execution quantity
                    exec_qty ← MIN(remaining_qty, sell_order.quantity)
                    
                    # Create execution
                    execution ← Trade{
                        buy_order_id: new_order.id,
                        sell_order_id: sell_order.id,
                        price: sell_order.price,
                        quantity: exec_qty,
                        timestamp: getCurrentNanotime()
                    }
                    executions.append(execution)
                    
                    # Update quantities
                    remaining_qty -= exec_qty
                    sell_order.quantity -= exec_qty
                    
                    IF sell_order.quantity == 0:
                        best_ask_level.orders.dequeue()
                    
                    # Risk check
                    IF violatesRiskLimits(new_order.account_id, execution):
                        remaining_qty ← 0  # Cancel rest
                        BREAK
                
                # Remove empty price level
                IF best_ask_level.orders.isEmpty():
                    order_book.asks.removeFirst()
        
        ELSE:  # SELL market order
            # Similar logic matching against bids
            matchMarketSellOrder(order_book, new_order, executions)
    
    ══════ Limit Order Matching ══════
    ELSE IF new_order.type == LIMIT:
        remaining ← matchLimitOrder(order_book, new_order, executions)
        
        # Add unmatched portion to book
        IF remaining > 0:
            insertIntoOrderBook(order_book, new_order, remaining)
    
    RETURN executions
END FUNCTION

▶ ALGORITHM PHASE 4: Order Book Maintenance
FUNCTION insertIntoOrderBook(order_book, order, quantity):
    
    ══════ Binary Search for Price Level ══════
    IF order.side == BUY:
        levels ← order_book.bids
        compare ← lambda a, b: b - a  # Descending
    ELSE:
        levels ← order_book.asks
        compare ← lambda a, b: a - b  # Ascending
    
    # Binary search for insertion point
    left ← 0
    right ← length(levels)
    
    WHILE left < right:
        mid ← (left + right) / 2
        
        IF compare(levels[mid].price, order.price) <= 0:
            right ← mid
        ELSE:
            left ← mid + 1
    
    # Check if price level exists
    IF left < length(levels) AND levels[left].price == order.price:
        # Add to existing level
        levels[left].orders.enqueue(order)
        levels[left].total_quantity += quantity
    ELSE:
        # Create new price level
        new_level ← PriceLevel{
            price: order.price,
            orders: Queue([order]),
            total_quantity: quantity
        }
        levels.insert(left, new_level)
END FUNCTION

▶ SPECIALIZED: Iceberg Order Handling
FUNCTION processIcebergOrder(order_book, iceberg_order):
    
    ══════ Hidden Quantity Management ══════
    visible_quantity ← iceberg_order.display_quantity
    hidden_quantity ← iceberg_order.total_quantity - visible_quantity
    
    # Create visible portion
    visible_order ← Order{
        id: iceberg_order.id,
        timestamp: iceberg_order.timestamp,
        side: iceberg_order.side,
        price: iceberg_order.price,
        quantity: visible_quantity,
        type: LIMIT
    }
    
    # Match visible portion
    executions ← matchOrders(order_book, visible_order)
    executed_qty ← SUM(exec.quantity FOR exec IN executions)
    
    # Replenish from hidden quantity
    WHILE hidden_quantity > 0 AND executed_qty > 0:
        replenish_qty ← MIN(hidden_quantity, executed_qty)
        
        # Create new visible order with new timestamp
        new_visible ← Order{
            id: generateOrderId(),
            timestamp: getCurrentNanotime(),  # Loses time priority
            side: iceberg_order.side,
            price: iceberg_order.price,
            quantity: replenish_qty,
            type: LIMIT
        }
        
        hidden_quantity -= replenish_qty
        
        # Try to match again
        new_executions ← matchOrders(order_book, new_visible)
        executions.extend(new_executions)
        executed_qty ← SUM(exec.quantity FOR exec IN new_executions)
    
    RETURN executions
END FUNCTION

▶ HIGH-FREQUENCY OPTIMIZATIONS:
FUNCTION lockFreeOrderBookUpdate(order_book, updates):
    
    ══════ Lock-Free Concurrent Updates ══════
    # Use atomic operations for HFT performance
    
    WHILE TRUE:
        current_version ← order_book.version.load(MEMORY_ORDER_ACQUIRE)
        
        # Create new version with updates
        new_book ← order_book.copy()
        
        FOR update IN updates:
            IF update.type == "ADD":
                insertAtomic(new_book, update.order)
            ELSE IF update.type == "CANCEL":
                removeAtomic(new_book, update.order_id)
            ELSE IF update.type == "MODIFY":
                modifyAtomic(new_book, update.order_id, update.new_quantity)
        
        # Try to commit using CAS
        IF order_book.version.compareAndSwap(
            current_version,
            current_version + 1,
            MEMORY_ORDER_ACQ_REL
        ):
            order_book.data.store(new_book, MEMORY_ORDER_RELEASE)
            BREAK
        
        # Retry on conflict
        backoff()
END FUNCTION

▶ MARKET DATA DISTRIBUTION:
FUNCTION generateMarketDataUpdate(executions, order_book):
    
    ══════ L1/L2/L3 Market Data ══════
    update ← MarketDataUpdate{
        timestamp: getCurrentNanotime(),
        symbol: order_book.symbol
    }
    
    # Level 1: Top of book
    IF NOT order_book.bids.isEmpty():
        update.best_bid ← order_book.bids[0].price
        update.best_bid_size ← order_book.bids[0].total_quantity
    
    IF NOT order_book.asks.isEmpty():
        update.best_ask ← order_book.asks[0].price
        update.best_ask_size ← order_book.asks[0].total_quantity
    
    # Level 2: Price level aggregates
    update.bid_levels ← []
    FOR level IN order_book.bids[:10]:  # Top 10 levels
        update.bid_levels.append({
            price: level.price,
            quantity: level.total_quantity,
            num_orders: length(level.orders)
        })
    
    update.ask_levels ← []
    FOR level IN order_book.asks[:10]:
        update.ask_levels.append({
            price: level.price,
            quantity: level.total_quantity,
            num_orders: length(level.orders)
        })
    
    # Level 3: Full order detail (for entitled subscribers)
    update.order_updates ← []
    FOR execution IN executions:
        update.order_updates.append({
            type: "TRADE",
            price: execution.price,
            quantity: execution.quantity,
            aggressor_side: determineAggressor(execution)
        })
    
    # VWAP calculation
    IF length(executions) > 0:
        total_value ← SUM(e.price × e.quantity FOR e IN executions)
        total_volume ← SUM(e.quantity FOR e IN executions)
        update.vwap ← total_value / total_volume
    
    RETURN update
END FUNCTION

▶ PERFORMANCE METRICS:
  • Latency: Wire-to-wire <1 microsecond
  • Throughput: 10M+ orders/second
  • Deterministic: Same input → same output
  • Memory: O(n) where n = active orders
  • Fair: Strict price-time priority
```

---

## Genomic Sequence Analysis

### 🧬 DNA/RNA Sequence Sorting (Suffix Array Construction)
**Purpose**: Enables fast pattern matching in genomic data
**Real Usage**: BLAST, BWA, Bowtie2, GATK genomic aligners

```pseudocode
╔════════════════════════════════════════════════════════════════════╗
║ ALGORITHM: SA-IS Suffix Array Construction for Genomic Data       ║
║ Genome Size: 3B bases | Construction: O(n) | Memory: 5n bytes     ║
╚════════════════════════════════════════════════════════════════════╝

▶ INPUT PARAMETERS:
  genome: string                     # DNA sequence (ACGT)
  build_lcp: boolean                 # Build LCP array
  build_bwt: boolean                 # Build BWT for compression
  
▶ OUTPUT:
  suffix_array: array[int]           # Sorted suffix positions
  lcp_array: array[int]              # Longest common prefix
  bwt: string                        # Burrows-Wheeler transform

▶ DATA STRUCTURES:
  Suffix: {
    position: int                   # Start position in genome
    length: int                     # Suffix length
    type: enum {L, S}               # L-type or S-type
  }

▶ ALGORITHM: SA-IS (Suffix Array by Induced Sorting)
FUNCTION buildSuffixArray(genome):
    
    ══════ STEP 1: Classify Suffixes ══════
    n ← length(genome)
    
    # Add sentinel character
    text ← genome + '$'
    
    # Classify each suffix as L-type or S-type
    types ← array[n + 1]
    types[n] ← 'S'  # Sentinel is S-type
    
    FOR i FROM n-1 DOWN TO 0:
        IF text[i] > text[i + 1]:
            types[i] ← 'L'
        ELSE IF text[i] < text[i + 1]:
            types[i] ← 'S'
        ELSE:
            types[i] ← types[i + 1]
    
    # Find LMS (Leftmost S) suffixes
    lms_suffixes ← []
    FOR i FROM 1 TO n:
        IF types[i] == 'S' AND types[i - 1] == 'L':
            lms_suffixes.append(i)
    
    ══════ STEP 2: Sort LMS Suffixes ══════
    # Create initial buckets for each character
    alphabet ← ['$', 'A', 'C', 'G', 'T']
    buckets ← createBuckets(text, alphabet)
    
    # Initialize suffix array
    sa ← array[n + 1]
    FILL(sa, -1)
    
    # Place LMS suffixes in their buckets
    FOR lms IN lms_suffixes:
        char ← text[lms]
        bucket_end ← buckets[char].end
        sa[bucket_end] ← lms
        buckets[char].end -= 1
    
    # Induce sort L-type suffixes
    induceSortL(sa, text, types, buckets)
    
    # Induce sort S-type suffixes
    induceSortS(sa, text, types, buckets)
    
    ══════ STEP 3: Recursive Sorting if Needed ══════
    # Check if all LMS suffixes are unique
    lms_names ← nameLMSSubstrings(sa, text, types, lms_suffixes)
    
    IF MAX(lms_names) < length(lms_suffixes) - 1:
        # Not all unique, need recursion
        reduced_text ← lms_names
        reduced_sa ← buildSuffixArray(reduced_text)
        
        # Map back to original positions
        FOR i, pos IN enumerate(reduced_sa):
            sa[i] ← lms_suffixes[pos]
    
    ══════ STEP 4: Final Induced Sorting ══════
    # Clear SA except for sorted LMS suffixes
    FOR i FROM 0 TO n:
        IF sa[i] NOT IN lms_suffixes:
            sa[i] ← -1
    
    # Place sorted LMS suffixes
    buckets ← createBuckets(text, alphabet)
    FOR i FROM n DOWN TO 0:
        IF sa[i] >= 0:
            char ← text[sa[i]]
            bucket_end ← buckets[char].end
            sa[bucket_end] ← sa[i]
            buckets[char].end -= 1
    
    # Final induced sorting
    induceSortL(sa, text, types, buckets)
    induceSortS(sa, text, types, buckets)
    
    RETURN sa[1:]  # Remove sentinel
    
    ══════ HELPER: Induced Sorting ══════
    FUNCTION induceSortL(sa, text, types, buckets):
        # Reset bucket starts
        FOR char IN buckets:
            buckets[char].start ← getbucketStart(char)
        
        FOR i FROM 0 TO length(sa)-1:
            IF sa[i] > 0:
                j ← sa[i] - 1
                IF types[j] == 'L':
                    char ← text[j]
                    sa[buckets[char].start] ← j
                    buckets[char].start += 1
    END FUNCTION
END FUNCTION

▶ BUILD LCP ARRAY (Kasai's Algorithm):
FUNCTION buildLCPArray(text, suffix_array):
    n ← length(text)
    lcp ← array[n]
    rank ← array[n]
    
    # Build rank array (inverse of suffix array)
    FOR i FROM 0 TO n-1:
        rank[suffix_array[i]] ← i
    
    h ← 0  # Current LCP value
    
    FOR i FROM 0 TO n-1:
        IF rank[i] > 0:
            j ← suffix_array[rank[i] - 1]
            
            # Compare suffixes starting at i and j
            WHILE i + h < n AND j + h < n AND text[i + h] == text[j + h]:
                h += 1
            
            lcp[rank[i]] ← h
            
            # Optimization: h decreases by at most 1
            IF h > 0:
                h -= 1
        ELSE:
            lcp[0] ← 0
    
    RETURN lcp
END FUNCTION

▶ PATTERN SEARCH USING SUFFIX ARRAY:
FUNCTION searchPattern(pattern, text, suffix_array):
    
    ══════ Binary Search on Suffix Array ══════
    n ← length(text)
    m ← length(pattern)
    
    # Find leftmost occurrence
    left ← 0
    right ← n
    
    WHILE left < right:
        mid ← (left + right) / 2
        suffix_start ← suffix_array[mid]
        
        comparison ← compareStrings(
            pattern,
            text[suffix_start:suffix_start + m]
        )
        
        IF comparison <= 0:
            right ← mid
        ELSE:
            left ← mid + 1
    
    first_match ← left
    
    # Find rightmost occurrence
    left ← 0
    right ← n
    
    WHILE left < right:
        mid ← (left + right) / 2
        suffix_start ← suffix_array[mid]
        
        comparison ← compareStrings(
            pattern,
            text[suffix_start:suffix_start + m]
        )
        
        IF comparison < 0:
            right ← mid
        ELSE:
            left ← mid + 1
    
    last_match ← left - 1
    
    # Extract all occurrences
    IF first_match <= last_match:
        occurrences ← []
        FOR i FROM first_match TO last_match:
            occurrences.append(suffix_array[i])
        RETURN SORT(occurrences)  # Sort by position
    
    RETURN []  # No matches
END FUNCTION

▶ SPECIALIZED: Burrows-Wheeler Transform
FUNCTION buildBWT(text, suffix_array):
    n ← length(text)
    bwt ← array[n]
    
    FOR i FROM 0 TO n-1:
        IF suffix_array[i] == 0:
            bwt[i] ← text[n - 1]  # Wrap around
        ELSE:
            bwt[i] ← text[suffix_array[i] - 1]
    
    RETURN bwt
END FUNCTION

▶ GENOMIC-SPECIFIC OPTIMIZATIONS:
FUNCTION compressedSuffixArray(genome):
    
    ══════ 2-bit Encoding for DNA ══════
    # Encode ACGT as 00, 01, 10, 11
    encoding ← {'A': 0b00, 'C': 0b01, 'G': 0b10, 'T': 0b11}
    
    compressed ← BitArray()
    FOR base IN genome:
        compressed.append(encoding[base], bits=2)
    
    # Build suffix array on compressed representation
    sa ← buildSuffixArrayCompressed(compressed)
    
    # Wavelet tree for rank/select queries
    wavelet_tree ← buildWaveletTree(compressed)
    
    RETURN CompressedIndex{
        suffix_array: sa,
        wavelet_tree: wavelet_tree,
        size_bytes: length(compressed) / 4  # 2 bits per base
    }
END FUNCTION

▶ PERFORMANCE NOTES:
  • Linear time O(n) construction
  • Cache-efficient for large genomes
  • Supports compressed indexes (FM-index)
  • Enables exact and approximate matching
  • Used in read alignment and assembly
```

---

## Social Media Feed Ranking

### 📱 Facebook/Twitter Timeline Sorting
**Purpose**: Ranks posts by relevance and engagement
**Real Usage**: Facebook News Feed, Twitter Timeline, Instagram Explore

```pseudocode
╔════════════════════════════════════════════════════════════════════╗
║ ALGORITHM: Time-Decay Ranking with Machine Learning Scores        ║
║ Posts: Millions | Update Rate: Real-time | Personalized: Yes      ║
╚════════════════════════════════════════════════════════════════════╝

▶ INPUT PARAMETERS:
  posts: array[Post]                 # Candidate posts
  user: UserProfile                  # Viewing user
  ml_model: RankingModel             # Trained neural network
  time_window: TimeRange             # Relevant time period
  
▶ OUTPUT:
  feed: array[Post]                  # Ranked timeline
  reasons: array[ExplanationCard]   # "Because you follow X"

▶ DATA STRUCTURES:
  Post: {
    id: string
    author_id: string
    timestamp: datetime
    content: string
    media: array[Media]
    engagement: {
      likes: int
      comments: int
      shares: int
      views: int
    }
    features: FeatureVector         # ML features
  }

▶ ALGORITHM:
FUNCTION rankSocialFeed(posts, user, ml_model, time_window):
    
    ══════ STEP 1: Feature Extraction ══════
    FOR post IN posts:
        post.features ← extractFeatures(post, user)
    
    FUNCTION extractFeatures(post, user):
        features ← {}
        
        # Engagement features
        features.like_rate ← post.likes / (post.views + 1)
        features.comment_rate ← post.comments / (post.views + 1)
        features.share_rate ← post.shares / (post.views + 1)
        
        # Time decay
        age_hours ← hoursSince(post.timestamp)
        features.recency ← exp(-age_hours / 24)  # Daily decay
        
        # Social features
        features.is_friend ← post.author_id IN user.friends
        features.is_family ← post.author_id IN user.family
        features.is_following ← post.author_id IN user.following
        
        # Affinity score
        features.affinity ← calculateAffinity(user, post.author_id)
        
        # Content features
        features.has_photo ← length(post.media.photos) > 0
        features.has_video ← length(post.media.videos) > 0
        features.text_length ← length(post.content)
        
        # Historical interaction
        features.user_clicked_author ← getClickRate(user, post.author_id)
        features.user_liked_similar ← getSimilarPostLikes(user, post)
        
        RETURN features
    END FUNCTION
    
    ══════ STEP 2: ML Scoring ══════
    # Batch score all posts
    feature_matrix ← createMatrix(post.features FOR post IN posts)
    ml_scores ← ml_model.predict(feature_matrix)
    
    FOR i, post IN enumerate(posts):
        post.ml_score ← ml_scores[i]
    
    ══════ STEP 3: Multi-Objective Sorting ══════
    FUNCTION hybridSort(posts):
        FOR post IN posts:
            # Combine multiple objectives
            relevance_score ← post.ml_score
            
            # Time decay with engagement boost
            time_score ← calculateTimeScore(post)
            
            # Diversity penalty
            diversity_score ← calculateDiversity(post, recent_shown)
            
            # Final score
            post.final_score ← (
                relevance_score × 0.5 +
                time_score × 0.3 +
                diversity_score × 0.2
            )
        
        # Modified quicksort with randomized pivot
        RETURN randomizedQuicksort(posts, key=final_score)
    END FUNCTION
    
    ══════ STEP 4: Business Logic Injection ══════
    sorted_posts ← hybridSort(posts)
    final_feed ← []
    
    # Ensure important posts appear
    FOR post IN sorted_posts:
        # Promotional content injection
        IF shouldInjectAd(final_feed):
            ad ← selectRelevantAd(user, final_feed)
            final_feed.append(ad)
        
        # Friend/family boost
        IF post.author_id IN user.close_connections:
            post.final_score *= 1.5
        
        # Demote negative signals
        IF post.hideRate > 0.1:
            post.final_score *= 0.5
        
        final_feed.append(post)
        
        # Story injection every 5 posts
        IF length(final_feed) % 5 == 0:
            stories ← getRelevantStories(user)
            IF length(stories) > 0:
                final_feed.append(StoryCard(stories))
    
    RETURN final_feed
END FUNCTION

▶ REAL-TIME SORTING UPDATE:
FUNCTION updateFeedRealtime(current_feed, new_post, user):
    
    ══════ Insertion Sort for Single Update ══════
    # Score new post
    new_post.features ← extractFeatures(new_post, user)
    new_post.ml_score ← ml_model.predict([new_post.features])[0]
    new_post.final_score ← calculateFinalScore(new_post)
    
    # Find insertion position
    position ← binarySearchPosition(current_feed, new_post.final_score)
    
    # Check if should be included
    IF position < MAX_FEED_SIZE:
        current_feed.insert(position, new_post)
        
        # Remove last if exceeding size
        IF length(current_feed) > MAX_FEED_SIZE:
            current_feed.pop()
    
    RETURN current_feed
END FUNCTION

▶ PERFORMANCE OPTIMIZATIONS:
  • Approximate scoring for tail content
  • Caching of ML predictions
  • Incremental feature updates
  • Parallel scoring across shards
  • Edge caching of ranked feeds
```

---

## E-Commerce Product Sorting

### 🛍️ Amazon/eBay Product Search Ranking
**Purpose**: Sorts products by relevance, price, ratings, and personalization
**Real Usage**: Amazon, eBay, Walmart, Alibaba product search

```pseudocode
╔════════════════════════════════════════════════════════════════════╗
║ ALGORITHM: Multi-Key Sorting with Faceted Search                  ║
║ Products: 100M+ | Response: <100ms | Personalized: Yes            ║
╚════════════════════════════════════════════════════════════════════╝

▶ INPUT PARAMETERS:
  products: array[Product]           # Search results
  sort_criteria: SortConfig          # Primary/secondary sort keys
  filters: array[Filter]             # Price range, brand, etc.
  user_profile: UserProfile          # Purchase history, preferences
  
▶ OUTPUT:
  sorted_products: array[Product]    # Final sorted list
  facets: FacetCounts               # Available filters with counts

▶ DATA STRUCTURES:
  Product: {
    id: string
    title: string
    price: decimal
    rating: float                   # 0-5 stars
    review_count: int
    sales_rank: int                 # Best seller rank
    prime_eligible: boolean
    availability: enum
    seller_rating: float
    relevance_score: float          # Search relevance
  }

▶ ALGORITHM:
FUNCTION sortProducts(products, sort_criteria, filters, user_profile):
    
    ══════ STEP 1: Apply Filters ══════
    filtered ← applyFilters(products, filters)
    
    ══════ STEP 2: Multi-Key Stable Sort ══════
    IF sort_criteria.type == "RELEVANCE":
        RETURN sortByRelevance(filtered, user_profile)
        
    ELSE IF sort_criteria.type == "PRICE":
        # Stable sort preserving relevance within price tiers
        RETURN stableMultiKeySort(filtered, [
            (lambda p: p.price, sort_criteria.order),
            (lambda p: p.relevance_score, DESC)
        ])
        
    ELSE IF sort_criteria.type == "RATING":
        # Bayesian average to handle review count
        FOR product IN filtered:
            # Avoid 5-star products with 1 review ranking highest
            C ← 10  # Smoothing constant
            m ← 3.5  # Prior mean rating
            
            product.bayesian_rating ← (
                (product.rating × product.review_count + m × C) /
                (product.review_count + C)
            )
        
        RETURN stableMultiKeySort(filtered, [
            (lambda p: p.bayesian_rating, DESC),
            (lambda p: p.review_count, DESC),
            (lambda p: p.relevance_score, DESC)
        ])
        
    ELSE IF sort_criteria.type == "PERSONALIZED":
        RETURN personalizedSort(filtered, user_profile)
    
    ══════ Stable Multi-Key Sort Implementation ══════
    FUNCTION stableMultiKeySort(items, sort_keys):
        # Sort by keys in reverse order (stable sort property)
        result ← items.copy()
        
        FOR key_func, order IN REVERSE(sort_keys):
            result ← stableSort(result, key_func, order)
        
        RETURN result
    END FUNCTION
    
    FUNCTION stableSort(items, key_func, order):
        # Use merge sort for stability
        IF length(items) <= 1:
            RETURN items
        
        mid ← length(items) / 2
        left ← stableSort(items[:mid], key_func, order)
        right ← stableSort(items[mid:], key_func, order)
        
        RETURN merge(left, right, key_func, order)
    END FUNCTION
END FUNCTION

▶ PERSONALIZED RANKING:
FUNCTION personalizedSort(products, user_profile):
    
    ══════ Calculate Personalization Scores ══════
    FOR product IN products:
        score ← 0
        
        # Purchase history similarity
        similar_purchases ← findSimilarPurchases(
            product,
            user_profile.purchase_history
        )
        score += length(similar_purchases) × 0.3
        
        # Brand affinity
        IF product.brand IN user_profile.preferred_brands:
            score += 0.2
        
        # Price range preference
        IF product.price BETWEEN user_profile.typical_price_range:
            score += 0.15
        
        # Category preferences
        FOR category IN product.categories:
            IF category IN user_profile.interests:
                score += user_profile.interests[category] × 0.1
        
        # Collaborative filtering
        cf_score ← collaborative_filter.score(user_profile, product)
        score += cf_score × 0.25
        
        product.personalization_score ← score
    
    # Sort by personalization
    RETURN SORT(products, key=lambda p: p.personalization_score, DESC)
END FUNCTION

▶ FACETED SEARCH COUNTING:
FUNCTION computeFacets(products):
    facets ← {
        "brand": HashMap(),
        "price_range": HashMap(),
        "rating": HashMap(),
        "features": HashMap()
    }
    
    FOR product IN products:
        # Brand facet
        facets.brand[product.brand] += 1
        
        # Price range facet
        price_bucket ← getPriceBucket(product.price)
        facets.price_range[price_bucket] += 1
        
        # Rating facet
        rating_bucket ← FLOOR(product.rating)
        facets.rating[f"{rating_bucket}+ stars"] += 1
        
        # Feature facets
        FOR feature IN product.features:
            facets.features[feature] += 1
    
    RETURN facets
END FUNCTION

▶ PERFORMANCE OPTIMIZATIONS:
  • Elasticsearch/Solr for distributed sorting
  • Bitmap indexes for fast filtering
  • Approximate sorting for tail results
  • Pre-computed sort orders for common queries
  • Caching with query fingerprinting
```

---

## Distributed TeraSort

### 🌐 MapReduce Large-Scale Sorting
**Purpose**: Sorts petabytes of data across thousands of machines
**Real Usage**: Hadoop, Spark, Google MapReduce, distributed databases

```pseudocode
╔════════════════════════════════════════════════════════════════════╗
║ ALGORITHM: Distributed Sample Sort with Range Partitioning        ║
║ Scale: Petabytes | Nodes: 1000+ | Time: O(n log n / p)            ║
╚════════════════════════════════════════════════════════════════════╝

▶ INPUT PARAMETERS:
  input_data: DistributedFile        # HDFS/S3 data
  num_reducers: int                  # Parallel sort partitions
  sample_rate: float                 # Sampling rate for pivots
  
▶ OUTPUT:
  sorted_output: DistributedFile     # Globally sorted data

▶ ALGORITHM:
FUNCTION teraSort(input_data, num_reducers):
    
    ══════ PHASE 1: Sampling for Partition Boundaries ══════
    FUNCTION sampleAndPartition():
        # Sample to find partition boundaries
        sample_size ← num_reducers × 1000
        samples ← []
        
        # Distributed sampling
        MAP PHASE (on each input split):
            local_samples ← []
            records_processed ← 0
            
            FOR record IN input_split:
                IF random() < sample_rate:
                    local_samples.append(record.key)
                
                records_processed += 1
                IF length(local_samples) >= sample_size / num_input_splits:
                    BREAK
            
            EMIT("sample", local_samples)
        
        REDUCE PHASE (single reducer):
            all_samples ← []
            FOR samples IN values:
                all_samples.extend(samples)
            
            # Sort samples
            all_samples ← SORT(all_samples)
            
            # Select partition boundaries
            boundaries ← []
            step ← length(all_samples) / num_reducers
            
            FOR i FROM 1 TO num_reducers-1:
                boundaries.append(all_samples[i × step])
            
            # Broadcast boundaries to all nodes
            BROADCAST(boundaries)
        
        RETURN boundaries
    END FUNCTION
    
    ══════ PHASE 2: Partitioned Sorting ══════
    boundaries ← sampleAndPartition()
    
    MAP PHASE (on each input split):
        # Load partition boundaries
        partitioner ← RangePartitioner(boundaries)
        
        FOR record IN input_split:
            # Determine target partition
            partition ← partitioner.getPartition(record.key)
            
            # Emit with composite key (partition, key)
            EMIT((partition, record.key), record.value)
    
    # Shuffle phase groups by partition
    
    REDUCE PHASE (one per partition):
        # Each reducer handles one partition
        partition_records ← []
        
        FOR (key, value) IN sorted_values:
            partition_records.append((key[1], value))  # Extract actual key
        
        # In-memory sort for this partition
        partition_records ← externalMergeSort(partition_records)
        
        # Write sorted partition
        FOR record IN partition_records:
            OUTPUT(record)
    
    ══════ PHASE 3: Verification (Optional) ══════
    FUNCTION verifyGlobalSort():
        previous_last ← NULL
        
        FOR partition IN range(num_reducers):
            partition_file ← getPartitionFile(partition)
            first_record ← partition_file.readFirst()
            
            IF previous_last != NULL:
                IF first_record.key < previous_last:
                    ERROR(f"Sort violation between partitions {partition-1} and {partition}")
            
            previous_last ← partition_file.readLast().key
        
        RETURN TRUE
    END FUNCTION
END FUNCTION

▶ OPTIMIZATIONS:
FUNCTION optimizedTeraSort(input_data, num_reducers):
    
    ══════ Combiner for Local Pre-Sorting ══════
    COMBINER PHASE:
        # Sort and combine locally before shuffle
        local_sorted ← []
        
        FOR (key, value) IN mapper_output:
            local_sorted.append((key, value))
        
        local_sorted ← SORT(local_sorted, key=lambda x: x[0])
        
        # Compress consecutive equal keys
        FOR key, group IN groupBy(local_sorted, key=lambda x: x[0]):
            combined_value ← combine(value FOR (k, value) IN group)
            EMIT(key, combined_value)
    
    ══════ Secondary Sort for Value Ordering ══════
    # Sort by (key, value) pairs
    PARTITIONER:
        # Partition only by key
        RETURN hash(key) % num_reducers
    
    GROUPING_COMPARATOR:
        # Group only by key
        RETURN compare(key1, key2)
    
    SORT_COMPARATOR:
        # Sort by key, then value
        IF key1 != key2:
            RETURN compare(key1, key2)
        ELSE:
            RETURN compare(value1, value2)
END FUNCTION

▶ FAULT TOLERANCE:
FUNCTION faultTolerantSort():
    # Speculative execution for stragglers
    FOR task IN running_tasks:
        IF task.progress < 0.5 × average_progress:
            # Launch backup task
            backup ← launchBackupTask(task)
            
            # Use first to complete
            winner ← waitForFirst([task, backup])
            kill(task IF winner == backup ELSE backup)
    
    # Checkpoint intermediate results
    IF partition_size > CHECKPOINT_THRESHOLD:
        writeCheckpoint(partial_results)
END FUNCTION

▶ PERFORMANCE METRICS:
  • Sort 1TB: ~3 minutes on 100 nodes
  • Sort 1PB: ~3 hours on 1000 nodes
  • Network shuffle: Optimized with compression
  • Memory: O(n/p) per node where p = partitions
  • Scalability: Linear with node count
```

## Summary

These real-world sorting algorithms demonstrate the diversity of sorting applications:

1. **Database External Sort**: Handles terabytes of data with limited memory
2. **Video Streaming**: Adaptive quality selection with real-time constraints  
3. **Search Ranking**: Multi-factor sorting with ML and personalization
4. **Financial Trading**: Microsecond-latency order matching with strict priority
5. **Genomic Analysis**: Linear-time suffix arrays for pattern matching
6. **Social Media**: Time-decay ranking with engagement optimization
7. **E-Commerce**: Multi-key sorting with faceted search
8. **Distributed Systems**: Petabyte-scale sorting across thousands of nodes

Each algorithm is optimized for its specific domain constraints—whether that's microsecond latency (trading), real-time updates (social media), or massive scale (distributed systems).