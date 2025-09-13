# Real-World Search Algorithms: Comprehensive Examples with Pseudocode

## Table of Contents
1. [Web Search Engine](#web-search-engine)
2. [GPS Navigation](#gps-navigation)
3. [Database Query Optimization](#database-query-optimization)
4. [Image Recognition Search](#image-recognition-search)
5. [Game AI Pathfinding](#game-ai-pathfinding)
6. [File System Search](#file-system-search)
7. [Similarity Search](#similarity-search)
8. [Network Routing](#network-routing)

---

## Web Search Engine

### 🔍 Google-Style Web Search (PageRank + Inverted Index)
**Purpose**: Ranks and retrieves web pages based on query relevance and authority
**Real Usage**: Google, Bing, DuckDuckGo search engines

```pseudocode
╔════════════════════════════════════════════════════════════════════╗
║ ALGORITHM: Web Search with PageRank and TF-IDF Ranking            ║
║ Scale: Billions of pages | Response Time: <200ms                  ║
╚════════════════════════════════════════════════════════════════════╝

▶ INPUT PARAMETERS:
  query: string                      # User search query
  web_graph: Graph[WebPage]          # Link structure of the web
  index: InvertedIndex               # Pre-built search index
  user_context: UserContext          # Location, search history, etc.
  
▶ OUTPUT:
  results: array[SearchResult]       # Ranked search results
  snippets: array[TextSnippet]       # Preview text for each result
  suggestions: array[string]         # Related search suggestions

▶ DATA STRUCTURES:
  WebPage: {
    url: string
    title: string
    content: string
    links: array[url]              # Outgoing links
    pagerank: float                # Pre-computed PageRank score
    last_crawled: datetime
    domain_authority: float
  }
  
  InvertedIndex: {
    terms: HashMap[string, PostingList]
    documents: HashMap[doc_id, DocumentInfo]
    bigrams: HashMap[pair, array[doc_id]]  # For phrase search
  }
  
  PostingList: {
    doc_frequency: int             # Number of docs containing term
    postings: array[Posting]       # Document occurrences
  }
  
  Posting: {
    doc_id: int
    term_frequency: int            # Occurrences in document
    positions: array[int]          # Word positions in document
    field_weights: map[field, weight]  # title:3.0, body:1.0, etc.
  }

▶ ALGORITHM PART 1: PageRank Computation (Offline)
FUNCTION computePageRank(web_graph, damping_factor=0.85, iterations=30):
    
    ══════ STEP 1: Initialize PageRank Values ══════
    N ← number_of_pages(web_graph)
    pagerank ← HashMap()
    
    # Start with uniform distribution
    FOR page IN web_graph.nodes():
        pagerank[page] ← 1.0 / N
    
    ══════ STEP 2: Build Adjacency Structure ══════
    # Create reverse index for incoming links
    incoming_links ← HashMap()
    outgoing_count ← HashMap()
    
    FOR page IN web_graph.nodes():
        outgoing_count[page] ← length(page.links)
        
        FOR target_url IN page.links:
            IF target_url NOT IN incoming_links:
                incoming_links[target_url] ← []
            incoming_links[target_url].append(page.url)
    
    ══════ STEP 3: Iterative PageRank Calculation ══════
    FOR iteration FROM 1 TO iterations:
        new_pagerank ← HashMap()
        
        FOR page IN web_graph.nodes():
            # Random surfer component
            rank ← (1 - damping_factor) / N
            
            # Incoming link contribution
            IF page.url IN incoming_links:
                FOR source_url IN incoming_links[page.url]:
                    source_pr ← pagerank[source_url]
                    out_links ← outgoing_count[source_url]
                    
                    IF out_links > 0:
                        rank += damping_factor × (source_pr / out_links)
            
            new_pagerank[page.url] ← rank
        
        # Check convergence
        delta ← 0
        FOR page IN web_graph.nodes():
            delta += ABS(new_pagerank[page.url] - pagerank[page.url])
        
        pagerank ← new_pagerank
        
        IF delta < 0.0001:  # Convergence threshold
            BREAK
    
    # Store PageRank in pages
    FOR page IN web_graph.nodes():
        page.pagerank ← pagerank[page.url]
    
    RETURN pagerank
END FUNCTION

▶ ALGORITHM PART 2: Query Processing and Search
FUNCTION searchWeb(query, index, web_graph, user_context):
    
    ══════ STEP 1: Query Analysis and Expansion ══════
    # Tokenize and normalize query
    query_terms ← tokenize(toLowerCase(query))
    query_terms ← removeStopWords(query_terms)
    
    # Spell correction
    corrected_terms ← []
    FOR term IN query_terms:
        IF term NOT IN index.terms:
            correction ← spellCorrect(term, index.terms.keys())
            corrected_terms.append(correction)
        ELSE:
            corrected_terms.append(term)
    
    # Query expansion with synonyms
    expanded_terms ← corrected_terms.copy()
    FOR term IN corrected_terms:
        synonyms ← getSynonyms(term, limit=2)
        expanded_terms.extend(synonyms)
    
    # Detect phrase queries (terms in quotes)
    phrases ← extractPhrases(query)
    
    ══════ STEP 2: Retrieve Candidate Documents ══════
    candidate_docs ← Set()
    term_doc_scores ← HashMap()  # doc_id -> term -> score
    
    FOR term IN expanded_terms:
        IF term NOT IN index.terms:
            CONTINUE
        
        posting_list ← index.terms[term]
        idf ← log(index.total_docs / posting_list.doc_frequency)
        
        FOR posting IN posting_list.postings:
            doc_id ← posting.doc_id
            candidate_docs.add(doc_id)
            
            # Calculate TF-IDF score
            tf ← 1 + log(posting.term_frequency)
            
            # Apply field boosts
            field_score ← 0
            FOR field, weight IN posting.field_weights:
                IF field == "title":
                    field_score += weight × 3.0  # Title boost
                ELSE IF field == "url":
                    field_score += weight × 2.0  # URL boost
                ELSE:
                    field_score += weight × 1.0  # Body text
            
            score ← tf × idf × field_score
            
            IF doc_id NOT IN term_doc_scores:
                term_doc_scores[doc_id] ← HashMap()
            term_doc_scores[doc_id][term] ← score
    
    # Handle phrase queries
    FOR phrase IN phrases:
        phrase_docs ← findPhraseDocuments(phrase, index)
        candidate_docs ← candidate_docs.intersection(phrase_docs)
    
    ══════ STEP 3: Score and Rank Documents ══════
    doc_scores ← []
    
    FOR doc_id IN candidate_docs:
        doc_info ← index.documents[doc_id]
        
        # BM25 scoring (improvement over TF-IDF)
        bm25_score ← 0
        k1 ← 1.2  # Term frequency saturation
        b ← 0.75  # Length normalization
        
        avg_doc_length ← index.average_doc_length
        doc_length ← doc_info.length
        
        FOR term IN corrected_terms:
            IF term IN term_doc_scores[doc_id]:
                tf ← term_doc_scores[doc_id][term]
                idf ← log((index.total_docs - posting_list.doc_frequency + 0.5) / 
                         (posting_list.doc_frequency + 0.5))
                
                norm_tf ← (tf × (k1 + 1)) / (tf + k1 × (1 - b + b × doc_length / avg_doc_length))
                bm25_score += idf × norm_tf
        
        # Combine with PageRank
        page ← web_graph.getPage(doc_info.url)
        pagerank_score ← page.pagerank × 100  # Scale PageRank
        
        # Additional signals
        freshness_score ← calculateFreshness(page.last_crawled)
        domain_score ← page.domain_authority
        
        # User context personalization
        personalization_score ← 0
        IF doc_info.url IN user_context.visited_urls:
            personalization_score += 0.1
        
        IF doc_info.domain IN user_context.preferred_domains:
            personalization_score += 0.2
        
        # Location relevance
        IF user_context.location:
            location_score ← calculateLocationRelevance(doc_info, user_context.location)
        ELSE:
            location_score ← 0
        
        # Combine all signals
        final_score ← (
            bm25_score × 0.4 +
            pagerank_score × 0.3 +
            domain_score × 0.1 +
            freshness_score × 0.1 +
            personalization_score × 0.05 +
            location_score × 0.05
        )
        
        doc_scores.append((doc_id, final_score))
    
    # Sort by score
    doc_scores ← SORT(doc_scores, key=score, descending=True)
    
    ══════ STEP 4: Generate Snippets and Results ══════
    results ← []
    snippets ← []
    
    FOR (doc_id, score) IN doc_scores[:10]:  # Top 10 results
        doc_info ← index.documents[doc_id]
        page ← web_graph.getPage(doc_info.url)
        
        # Generate snippet with query term highlighting
        snippet ← generateSnippet(
            page.content,
            corrected_terms,
            context_window=150  # characters
        )
        
        result ← SearchResult{
            url: page.url,
            title: page.title,
            score: score,
            snippet: snippet,
            cached_date: page.last_crawled
        }
        
        results.append(result)
        snippets.append(snippet)
    
    ══════ STEP 5: Generate Search Suggestions ══════
    suggestions ← []
    
    # Related searches based on co-occurrence
    related_terms ← findRelatedTerms(corrected_terms, index)
    FOR term IN related_terms[:5]:
        suggestion ← query + " " + term
        suggestions.append(suggestion)
    
    # Popular refinements from query logs
    refinements ← getPopularRefinements(query, user_context)
    suggestions.extend(refinements[:3])
    
    RETURN results, snippets, suggestions
END FUNCTION

▶ HELPER FUNCTIONS:
FUNCTION generateSnippet(content, query_terms, context_window):
    # Find best passage containing query terms
    sentences ← splitIntoSentences(content)
    best_score ← -1
    best_snippet ← ""
    
    FOR i FROM 0 TO length(sentences)-1:
        window ← sentences[MAX(0, i-1):MIN(length(sentences), i+2)]
        window_text ← JOIN(window, " ")
        
        # Count query term occurrences
        score ← 0
        FOR term IN query_terms:
            score += countOccurrences(toLowerCase(window_text), term)
        
        # Prefer earlier passages (more relevant)
        position_penalty ← i / length(sentences)
        score ← score × (1 - 0.3 × position_penalty)
        
        IF score > best_score:
            best_score ← score
            best_snippet ← window_text[:context_window]
    
    # Highlight query terms
    FOR term IN query_terms:
        best_snippet ← REPLACE(best_snippet, term, "<b>" + term + "</b>")
    
    RETURN best_snippet + "..."
END FUNCTION

FUNCTION findPhraseDocuments(phrase, index):
    phrase_terms ← tokenize(phrase)
    
    IF length(phrase_terms) < 2:
        RETURN Set()
    
    # Get documents containing all terms
    doc_sets ← []
    FOR term IN phrase_terms:
        IF term IN index.terms:
            docs ← Set(posting.doc_id FOR posting IN index.terms[term].postings)
            doc_sets.append(docs)
    
    # Intersection of all term documents
    common_docs ← doc_sets[0]
    FOR doc_set IN doc_sets[1:]:
        common_docs ← common_docs.intersection(doc_set)
    
    # Verify phrase adjacency
    phrase_docs ← Set()
    FOR doc_id IN common_docs:
        IF verifyPhraseInDocument(doc_id, phrase_terms, index):
            phrase_docs.add(doc_id)
    
    RETURN phrase_docs
END FUNCTION

▶ OPTIMIZATION TECHNIQUES:
  • Shard index across multiple servers
  • Use bloom filters for quick existence checks
  • Cache popular query results
  • Implement early termination for top-k retrieval
  • Use SIMD instructions for scoring
  • Compress posting lists with variable-byte encoding
```

---

## GPS Navigation

### 🗺️ Real-Time GPS Navigation (A* with Dynamic Traffic)
**Purpose**: Finds optimal driving routes considering real-time traffic
**Real Usage**: Google Maps, Waze, Apple Maps

```pseudocode
╔════════════════════════════════════════════════════════════════════╗
║ ALGORITHM: A* Pathfinding with Traffic and Constraints            ║
║ Graph Size: ~50M nodes | Update Rate: 1Hz | Accuracy: 95%         ║
╚════════════════════════════════════════════════════════════════════╝

▶ INPUT PARAMETERS:
  start: Coordinates                 # Starting GPS location
  destination: Coordinates           # Target GPS location
  road_network: Graph[RoadSegment]   # Street map graph
  traffic_data: TrafficMap           # Real-time traffic speeds
  preferences: RoutePreferences      # Avoid tolls, highways, etc.
  departure_time: datetime           # For predictive traffic
  
▶ OUTPUT:
  route: array[RoadSegment]          # Optimal path
  distance: float                    # Total distance in km
  duration: int                      # Estimated time in seconds
  alternatives: array[Route]         # Alternative routes
  turn_instructions: array[string]   # Navigation instructions

▶ DATA STRUCTURES:
  RoadSegment: {
    id: string
    start_node: NodeID
    end_node: NodeID
    length: float                   # Segment length in meters
    speed_limit: int                # Posted speed in km/h
    road_type: enum                 # highway, arterial, residential
    lanes: int
    restrictions: array[string]     # "no_trucks", "toll", etc.
    geometry: array[Coordinates]    # Shape points
  }
  
  Node: {
    id: NodeID
    location: Coordinates
    edges: array[RoadSegment]       # Outgoing road segments
    traffic_lights: boolean
    elevation: float                # For fuel efficiency
  }
  
  TrafficData: {
    segment_id: string
    current_speed: float            # Current average speed
    historical_speed: array[float]  # By hour of day
    incidents: array[Incident]      # Accidents, construction
    congestion_level: int           # 0-10 scale
  }
  
  SearchNode: {
    node_id: NodeID
    g_cost: float                   # Cost from start
    h_cost: float                   # Heuristic to goal
    f_cost: float                   # g + h
    parent: SearchNode
    arrival_time: datetime
  }

▶ ALGORITHM:
FUNCTION findRoute(start, destination, road_network, traffic_data, preferences, departure_time):
    
    ══════ STEP 1: Map Matching - Snap GPS to Road ══════
    start_node ← findNearestRoadNode(start, road_network)
    dest_node ← findNearestRoadNode(destination, road_network)
    
    IF start_node == NULL OR dest_node == NULL:
        RETURN ERROR("Location not accessible by road")
    
    ══════ STEP 2: Preprocess Graph Based on Constraints ══════
    # Build filtered graph excluding restricted roads
    valid_segments ← []
    
    FOR segment IN road_network.segments:
        # Check user preferences
        IF preferences.avoid_tolls AND "toll" IN segment.restrictions:
            CONTINUE
        
        IF preferences.avoid_highways AND segment.road_type == "highway":
            CONTINUE
        
        IF preferences.vehicle_type == "truck":
            IF "no_trucks" IN segment.restrictions:
                CONTINUE
            IF segment.height_limit < preferences.vehicle_height:
                CONTINUE
        
        valid_segments.append(segment)
    
    ══════ STEP 3: Hierarchical A* Search ══════
    # Use contraction hierarchies for long-distance routing
    IF distance(start, destination) > 50:  # km
        contracted_graph ← getContractedGraph(road_network)
        USE contracted_graph FOR initial_search
    
    # Initialize A* data structures
    open_set ← PriorityQueue()  # Min-heap by f_cost
    closed_set ← Set()
    node_costs ← HashMap()      # Best known g_cost for each node
    
    # Create start node
    start_search_node ← SearchNode{
        node_id: start_node,
        g_cost: 0,
        h_cost: haversineDistance(start_node.location, dest_node.location),
        f_cost: h_cost,
        parent: NULL,
        arrival_time: departure_time
    }
    
    open_set.push(start_search_node)
    node_costs[start_node] ← 0
    
    ══════ STEP 4: A* Main Loop with Traffic ══════
    WHILE NOT open_set.isEmpty():
        current ← open_set.pop()  # Node with lowest f_cost
        
        # Goal test
        IF current.node_id == dest_node:
            RETURN reconstructPath(current)
        
        closed_set.add(current.node_id)
        
        # Expand neighbors
        FOR edge IN road_network.getOutgoingEdges(current.node_id):
            neighbor_id ← edge.end_node
            
            IF neighbor_id IN closed_set:
                CONTINUE
            
            # Calculate edge cost with real-time traffic
            edge_cost ← calculateEdgeCost(
                edge,
                traffic_data,
                current.arrival_time,
                preferences
            )
            
            tentative_g ← current.g_cost + edge_cost
            
            # Check if we found a better path
            IF neighbor_id IN node_costs:
                IF tentative_g >= node_costs[neighbor_id]:
                    CONTINUE  # Not a better path
            
            node_costs[neighbor_id] ← tentative_g
            
            # Calculate arrival time at neighbor
            travel_time ← calculateTravelTime(edge, traffic_data, current.arrival_time)
            arrival_time ← current.arrival_time + travel_time
            
            # Advanced heuristic considering traffic patterns
            h_cost ← calculateHeuristic(
                neighbor_id,
                dest_node,
                arrival_time,
                traffic_data
            )
            
            neighbor_node ← SearchNode{
                node_id: neighbor_id,
                g_cost: tentative_g,
                h_cost: h_cost,
                f_cost: tentative_g + h_cost,
                parent: current,
                arrival_time: arrival_time
            }
            
            open_set.push(neighbor_node)
        
        # Timeout check for real-time responsiveness
        IF elapsed_time() > 1000:  # milliseconds
            RETURN getBestPartialPath(open_set, dest_node)
    
    RETURN NULL  # No path found
    
    ══════ STEP 5: Path Reconstruction and Instructions ══════
    FUNCTION reconstructPath(goal_node):
        path ← []
        current ← goal_node
        total_distance ← 0
        total_duration ← 0
        
        WHILE current.parent != NULL:
            parent ← current.parent
            segment ← road_network.getSegment(parent.node_id, current.node_id)
            path.prepend(segment)
            
            total_distance += segment.length
            travel_time ← current.arrival_time - parent.arrival_time
            total_duration += travel_time
            
            current ← parent
        
        # Generate turn-by-turn instructions
        instructions ← generateInstructions(path)
        
        # Find alternative routes
        alternatives ← findAlternativeRoutes(
            start_node,
            dest_node,
            path,
            road_network,
            traffic_data
        )
        
        RETURN Route{
            segments: path,
            distance: total_distance / 1000,  # Convert to km
            duration: total_duration,
            instructions: instructions,
            alternatives: alternatives
        }
    END FUNCTION
END FUNCTION

▶ HELPER FUNCTIONS:
FUNCTION calculateEdgeCost(edge, traffic_data, current_time, preferences):
    base_cost ← edge.length  # Distance in meters
    
    # Get current traffic speed
    traffic ← traffic_data.getSegmentTraffic(edge.id)
    
    IF traffic != NULL:
        current_speed ← traffic.current_speed
        
        # Predict future traffic when we'll reach this segment
        IF preferences.use_predictive:
            predicted_speed ← predictTrafficSpeed(
                traffic,
                current_time,
                edge.id
            )
            current_speed ← predicted_speed
    ELSE:
        # Use default speed for road type
        current_speed ← getDefaultSpeed(edge.road_type)
    
    # Time-based cost
    time_cost ← edge.length / (current_speed / 3.6)  # Convert km/h to m/s
    
    # Apply preference weights
    cost ← 0
    
    IF preferences.optimize_for == "time":
        cost ← time_cost
    ELSE IF preferences.optimize_for == "distance":
        cost ← base_cost
    ELSE IF preferences.optimize_for == "fuel":
        # Consider elevation changes and stop-and-go traffic
        fuel_factor ← calculateFuelEfficiency(
            edge,
            current_speed,
            traffic.congestion_level
        )
        cost ← base_cost × fuel_factor
    
    # Penalties for undesirable road features
    IF edge.road_type == "residential" AND preferences.prefer_highways:
        cost *= 1.5
    
    IF "construction" IN traffic.incidents:
        cost *= 2.0
    
    IF edge.hasTrafficLight():
        cost += 30  # Average traffic light delay in seconds
    
    RETURN cost
END FUNCTION

FUNCTION calculateHeuristic(node, goal, arrival_time, traffic_data):
    # Haversine distance as base heuristic
    straight_distance ← haversineDistance(node.location, goal.location)
    
    # Estimate speed based on distance to goal
    IF straight_distance > 10000:  # Over 10km - likely highway
        estimated_speed ← 80  # km/h
    ELSE IF straight_distance > 2000:  # 2-10km - arterial roads
        estimated_speed ← 50
    ELSE:  # Under 2km - local streets
        estimated_speed ← 30
    
    # Adjust for time of day traffic patterns
    hour ← arrival_time.hour
    IF hour IN [7, 8, 17, 18]:  # Rush hour
        estimated_speed *= 0.6
    ELSE IF hour IN [9, 10, 15, 16]:  # Moderate traffic
        estimated_speed *= 0.8
    
    # Convert to time estimate
    time_estimate ← straight_distance / (estimated_speed / 3.6)
    
    RETURN time_estimate
END FUNCTION

FUNCTION generateInstructions(path):
    instructions ← []
    
    FOR i FROM 0 TO length(path)-1:
        segment ← path[i]
        
        IF i == 0:
            instructions.append(f"Head {getCardinalDirection(segment)} on {segment.name}")
        ELSE:
            prev_segment ← path[i-1]
            angle ← calculateTurnAngle(prev_segment, segment)
            
            IF ABS(angle) < 20:
                instruction ← f"Continue on {segment.name}"
            ELSE IF angle > 0:
                IF ABS(angle) > 135:
                    instruction ← f"Make a U-turn onto {segment.name}"
                ELSE IF ABS(angle) > 60:
                    instruction ← f"Turn right onto {segment.name}"
                ELSE:
                    instruction ← f"Bear right onto {segment.name}"
            ELSE:
                IF ABS(angle) > 135:
                    instruction ← f"Make a U-turn onto {segment.name}"
                ELSE IF ABS(angle) > 60:
                    instruction ← f"Turn left onto {segment.name}"
                ELSE:
                    instruction ← f"Bear left onto {segment.name}"
            
            # Add distance
            instruction += f" and continue for {segment.length}m"
            instructions.append(instruction)
    
    instructions.append(f"Arrive at destination")
    
    RETURN instructions
END FUNCTION

FUNCTION findAlternativeRoutes(start, dest, primary_route, network, traffic):
    alternatives ← []
    
    # Use penalty method - increase cost of primary route segments
    FOR segment IN primary_route:
        segment.temp_penalty ← segment.cost × 1.5
    
    # Find up to 2 alternatives
    FOR i FROM 0 TO 1:
        alt_route ← findRoute(start, dest, network, traffic, preferences, departure_time)
        
        IF alt_route != NULL AND alt_route != primary_route:
            # Check if sufficiently different (share < 70% of segments)
            overlap ← calculateOverlap(primary_route, alt_route)
            IF overlap < 0.7:
                alternatives.append(alt_route)
                
                # Penalize this alternative for next iteration
                FOR segment IN alt_route:
                    segment.temp_penalty ← segment.cost × 1.3
    
    # Remove temporary penalties
    FOR segment IN network.segments:
        segment.temp_penalty ← 0
    
    RETURN alternatives
END FUNCTION

▶ OPTIMIZATIONS:
  • Bidirectional search for faster convergence
  • Contraction hierarchies for long-distance routing
  • Arc flags for region-based pruning
  • Precomputed shortest path hints
  • Partial path caching for common routes
  • Parallel search for alternatives
```

---

## Database Query Optimization

### 💾 SQL Query Execution (B+ Tree Index Search)
**Purpose**: Efficiently retrieves data from massive databases
**Real Usage**: PostgreSQL, MySQL, Oracle, SQL Server

```pseudocode
╔════════════════════════════════════════════════════════════════════╗
║ ALGORITHM: B+ Tree Index Search with Query Optimization           ║
║ Scale: Billions of rows | Response: <10ms | Memory: O(log n)      ║
╚════════════════════════════════════════════════════════════════════╝

▶ INPUT PARAMETERS:
  query: SQLQuery                    # Parsed SQL SELECT statement
  table: Table                       # Database table
  indexes: array[BPlusTree]          # Available indexes
  statistics: TableStatistics        # Cardinality, selectivity info
  buffer_pool: BufferPool            # Page cache
  
▶ OUTPUT:
  result_set: array[Row]             # Query results
  execution_plan: QueryPlan          # Optimized execution plan
  statistics: QueryStats             # Rows examined, time taken

▶ DATA STRUCTURES:
  BPlusTree: {
    root: BPlusNode
    order: int                      # Maximum children per node
    key_type: DataType
    leaf_level: int                 # Height of tree
    num_keys: long                  # Total keys in index
  }
  
  BPlusNode: {
    is_leaf: boolean
    keys: array[KeyValue]           # Sorted keys
    children: array[BPlusNode]      # Child pointers (internal nodes)
    records: array[RowPointer]      # Data pointers (leaf nodes)
    next_leaf: BPlusNode            # Next leaf for range scans
    parent: BPlusNode
  }
  
  QueryPlan: {
    operation: enum                 # INDEX_SCAN, TABLE_SCAN, NESTED_LOOP, etc.
    cost: float                     # Estimated cost
    rows: long                      # Estimated rows
    index_used: string
    filter_predicates: array[Predicate]
  }

▶ ALGORITHM PART 1: Query Optimization
FUNCTION optimizeQuery(query, table, indexes, statistics):
    
    ══════ STEP 1: Parse and Analyze Predicates ══════
    predicates ← extractPredicates(query.WHERE)
    join_conditions ← extractJoins(query.FROM)
    
    # Classify predicates
    equality_predicates ← []
    range_predicates ← []
    complex_predicates ← []
    
    FOR predicate IN predicates:
        IF predicate.operator == "=":
            equality_predicates.append(predicate)
        ELSE IF predicate.operator IN ["<", ">", "<=", ">=", "BETWEEN"]:
            range_predicates.append(predicate)
        ELSE:
            complex_predicates.append(predicate)
    
    ══════ STEP 2: Index Selection ══════
    candidate_plans ← []
    
    # Consider each available index
    FOR index IN indexes:
        IF canUseIndex(index, predicates):
            plan ← createIndexPlan(index, predicates, statistics)
            candidate_plans.append(plan)
    
    # Consider full table scan
    table_scan_plan ← createTableScanPlan(table, predicates, statistics)
    candidate_plans.append(table_scan_plan)
    
    # Consider composite index usage
    FOR index IN indexes:
        IF index.is_composite:
            # Check if we can use index for sorting
            IF matchesOrderBy(index, query.ORDER_BY):
                plan ← createIndexOrderPlan(index, predicates, statistics)
                plan.cost *= 0.8  # Prefer index that avoids sorting
                candidate_plans.append(plan)
    
    ══════ STEP 3: Cost Estimation ══════
    FOR plan IN candidate_plans:
        # I/O cost estimation
        if plan.operation == "INDEX_SCAN":
            index_height ← plan.index.leaf_level
            index_selectivity ← estimateSelectivity(predicates, statistics)
            
            # Cost = tree traversal + leaf scan + data fetch
            tree_cost ← index_height  # Page reads to reach leaf
            leaf_cost ← CEIL(plan.index.num_keys × index_selectivity / keys_per_page)
            data_cost ← plan.rows  # Assume random I/O for data pages
            
            plan.cost ← tree_cost + leaf_cost + data_cost × random_io_factor
            
        ELSE IF plan.operation == "TABLE_SCAN":
            pages ← table.num_pages
            plan.cost ← pages × sequential_io_factor
            
            # Apply filter selectivity
            selectivity ← estimateSelectivity(predicates, statistics)
            plan.rows ← table.num_rows × selectivity
    
    # Select best plan
    best_plan ← MIN(candidate_plans, key=lambda p: p.cost)
    
    RETURN best_plan
END FUNCTION

▶ ALGORITHM PART 2: B+ Tree Search Execution
FUNCTION executeIndexSearch(index, search_key, operation, buffer_pool):
    
    ══════ STEP 1: Tree Traversal to Leaf ══════
    current ← index.root
    path ← []  # For potential node splits
    
    WHILE NOT current.is_leaf:
        path.append(current)
        
        # Binary search within node
        child_index ← binarySearchNode(current, search_key, operation)
        
        # Pin page in buffer pool
        child_page_id ← current.children[child_index].page_id
        child_page ← buffer_pool.getPage(child_page_id)
        
        IF child_page == NULL:
            # Page not in memory, fetch from disk
            child_page ← readPageFromDisk(child_page_id)
            buffer_pool.addPage(child_page)
        
        current ← deserializeNode(child_page)
    
    ══════ STEP 2: Leaf Level Search ══════
    IF operation == "EQUAL":
        # Point query
        key_index ← binarySearchLeaf(current, search_key)
        
        IF key_index >= 0 AND current.keys[key_index] == search_key:
            RETURN [current.records[key_index]]
        ELSE:
            RETURN []  # Not found
    
    ELSE IF operation == "RANGE":
        # Range query
        results ← []
        start_key, end_key ← search_key  # Tuple of (min, max)
        
        # Find starting position
        start_index ← binarySearchLeaf(current, start_key)
        IF start_index < 0:
            start_index ← -(start_index + 1)  # Insertion point
        
        # Scan leaf nodes
        WHILE current != NULL:
            FOR i FROM start_index TO length(current.keys)-1:
                IF current.keys[i] > end_key:
                    RETURN results  # Exceeded range
                
                IF current.keys[i] >= start_key:
                    results.append(current.records[i])
            
            # Move to next leaf
            current ← current.next_leaf
            start_index ← 0  # Start from beginning of next leaf
            
            # Check for early termination
            IF current != NULL AND current.keys[0] > end_key:
                BREAK
        
        RETURN results
    
    ELSE IF operation IN ["GREATER", "GREATER_EQUAL", "LESS", "LESS_EQUAL"]:
        # Half-range query
        results ← []
        
        IF operation IN ["GREATER", "GREATER_EQUAL"]:
            # Scan forward from search_key
            start_index ← binarySearchLeaf(current, search_key)
            IF start_index < 0:
                start_index ← -(start_index + 1)
            
            IF operation == "GREATER":
                start_index += 1  # Exclude equal values
            
            WHILE current != NULL:
                FOR i FROM start_index TO length(current.keys)-1:
                    results.append(current.records[i])
                
                current ← current.next_leaf
                start_index ← 0
        
        ELSE:  # LESS or LESS_EQUAL
            # Scan from beginning up to search_key
            current ← findLeftmostLeaf(index.root)
            
            WHILE current != NULL:
                FOR i FROM 0 TO length(current.keys)-1:
                    IF operation == "LESS" AND current.keys[i] >= search_key:
                        RETURN results
                    IF operation == "LESS_EQUAL" AND current.keys[i] > search_key:
                        RETURN results
                    
                    results.append(current.records[i])
                
                current ← current.next_leaf
        
        RETURN results
END FUNCTION

▶ HELPER FUNCTIONS:
FUNCTION binarySearchNode(node, key, operation):
    # Binary search for child pointer in internal node
    left ← 0
    right ← length(node.keys) - 1
    
    WHILE left <= right:
        mid ← (left + right) / 2
        
        IF key == node.keys[mid]:
            IF operation IN ["GREATER", "GREATER_EQUAL"]:
                RETURN mid + 1  # Go right for greater values
            ELSE:
                RETURN mid  # Go left for less/equal values
        
        ELSE IF key < node.keys[mid]:
            right ← mid - 1
        ELSE:
            left ← mid + 1
    
    RETURN left  # Child index for key insertion point
END FUNCTION

FUNCTION binarySearchLeaf(leaf, key):
    # Binary search in leaf node
    left ← 0
    right ← length(leaf.keys) - 1
    
    WHILE left <= right:
        mid ← (left + right) / 2
        
        IF key == leaf.keys[mid]:
            RETURN mid
        ELSE IF key < leaf.keys[mid]:
            right ← mid - 1
        ELSE:
            left ← mid + 1
    
    RETURN -(left + 1)  # Negative indicates insertion point
END FUNCTION

▶ ALGORITHM PART 3: Join Processing
FUNCTION executeJoin(left_table, right_table, join_condition, indexes):
    
    ══════ Choose Join Algorithm ══════
    left_size ← left_table.num_rows
    right_size ← right_table.num_rows
    
    # Check for index on join column
    right_index ← findIndex(indexes, right_table, join_condition.right_column)
    left_index ← findIndex(indexes, left_table, join_condition.left_column)
    
    IF right_index != NULL AND left_size < right_size:
        RETURN indexNestedLoopJoin(left_table, right_table, join_condition, right_index)
    ELSE IF left_size + right_size < available_memory:
        RETURN hashJoin(left_table, right_table, join_condition)
    ELSE:
        RETURN sortMergeJoin(left_table, right_table, join_condition)
END FUNCTION

FUNCTION indexNestedLoopJoin(outer, inner, condition, index):
    results ← []
    
    FOR outer_row IN outer.scan():
        join_key ← outer_row[condition.left_column]
        
        # Use index to find matching inner rows
        matching_rows ← executeIndexSearch(index, join_key, "EQUAL", buffer_pool)
        
        FOR inner_row IN matching_rows:
            IF evaluateJoinCondition(outer_row, inner_row, condition):
                combined_row ← concatenate(outer_row, inner_row)
                results.append(combined_row)
    
    RETURN results
END FUNCTION

FUNCTION hashJoin(left, right, condition):
    # Build phase
    hash_table ← HashMap()
    
    FOR row IN right.scan():  # Build on smaller table
        key ← row[condition.right_column]
        IF key NOT IN hash_table:
            hash_table[key] ← []
        hash_table[key].append(row)
    
    # Probe phase
    results ← []
    
    FOR row IN left.scan():
        key ← row[condition.left_column]
        IF key IN hash_table:
            FOR matching_row IN hash_table[key]:
                combined ← concatenate(row, matching_row)
                results.append(combined)
    
    RETURN results
END FUNCTION

▶ OPTIMIZATION TECHNIQUES:
  • Index-only scans (covering indexes)
  • Bitmap indexes for low-cardinality columns
  • Partition pruning for large tables
  • Parallel query execution
  • Adaptive query optimization
  • Join order optimization
  • Predicate pushdown
  • Lazy evaluation for LIMIT queries
```