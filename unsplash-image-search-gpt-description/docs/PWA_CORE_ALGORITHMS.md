# PWA Core Algorithms - Pseudocode Specifications

## SPARC Pseudocode Phase: Offline-First PWA with Supabase Integration

This document contains comprehensive pseudocode for the core algorithms needed to transform the existing desktop application into a Progressive Web App (PWA) with offline-first capabilities and Supabase backend integration.

---

## 1. OFFLINE-FIRST SYNC ALGORITHM

### Overview
Manages seamless synchronization between local IndexedDB storage and Supabase backend, ensuring full offline functionality with automatic conflict resolution.

```
ALGORITHM: OfflineFirstSyncManager
INPUT: None (manages global state)
OUTPUT: Synchronized data state

CONSTANTS:
    MAX_RETRY_ATTEMPTS = 3
    SYNC_BATCH_SIZE = 50
    HEARTBEAT_INTERVAL = 30000  // 30 seconds
    CONFLICT_RESOLUTION_STRATEGY = "last_write_wins"  // or "crdt"

DATA STRUCTURES:
    SyncQueue: Priority Queue
        - operations: [{id, type, data, timestamp, retryCount}]
        - priority: "create" > "update" > "delete"
    
    ConflictResolver: Strategy Pattern
        - lastWriteWins()
        - crdtMerge()
        - userPromptResolution()

    LocalDB: IndexedDB Interface
        - vocabulary: {id, word, translation, timestamp, syncStatus}
        - images: {id, url, metadata, cached, timestamp}
        - sessions: {id, data, lastModified, syncStatus}

BEGIN_ALGORITHM: OfflineFirstSyncManager

    INITIALIZATION:
        connection ← NetworkConnection()
        localDB ← IndexedDBManager()
        supabase ← SupabaseClient()
        syncQueue ← PriorityQueue()
        syncState ← {lastSync: null, pendingOps: 0, conflicts: []}

    FUNCTION: detectNetworkStatus()
        IF navigator.onLine AND canReachSupabase() THEN
            RETURN "online"
        ELSE
            RETURN "offline"
        END IF
    END FUNCTION

    FUNCTION: queueOperation(operation)
        operation.id ← generateUUID()
        operation.timestamp ← getCurrentTimestamp()
        operation.retryCount ← 0
        operation.syncStatus ← "pending"
        
        // Store locally immediately
        localDB.store(operation.type, operation.data)
        
        // Add to sync queue
        syncQueue.enqueue(operation, getPriority(operation.type))
        
        // Trigger sync if online
        IF detectNetworkStatus() === "online" THEN
            scheduleSync()
        END IF
    END FUNCTION

    FUNCTION: syncWithSupabase()
        IF detectNetworkStatus() === "offline" THEN
            scheduleRetrySync(HEARTBEAT_INTERVAL)
            RETURN "sync_deferred"
        END IF

        conflictsFound ← []
        operationsProcessed ← 0
        
        WHILE NOT syncQueue.isEmpty() AND operationsProcessed < SYNC_BATCH_SIZE DO
            operation ← syncQueue.dequeue()
            
            TRY
                result ← executeSupabaseOperation(operation)
                
                IF result.success THEN
                    localDB.markSynced(operation.id)
                    operationsProcessed ← operationsProcessed + 1
                ELSE IF result.conflict THEN
                    conflict ← resolveConflict(operation, result.serverData)
                    conflictsFound.append(conflict)
                ELSE
                    handleSyncError(operation, result.error)
                END IF
                
            CATCH NetworkError e
                requeue(operation)
                RETURN "network_error"
            CATCH SupabaseError e
                handleSupabaseError(operation, e)
            END TRY
        END WHILE
        
        // Handle conflicts after batch processing
        FOR EACH conflict IN conflictsFound DO
            resolveAndApply(conflict)
        END FOR
        
        // Update sync metadata
        updateSyncTimestamp()
        
        RETURN "sync_complete"
    END FUNCTION

    FUNCTION: resolveConflict(localOperation, serverData)
        BEGIN
            IF CONFLICT_RESOLUTION_STRATEGY === "last_write_wins" THEN
                IF localOperation.timestamp > serverData.updated_at THEN
                    RETURN {resolution: "use_local", data: localOperation.data}
                ELSE
                    RETURN {resolution: "use_server", data: serverData}
                END IF
                
            ELSE IF CONFLICT_RESOLUTION_STRATEGY === "crdt" THEN
                mergedData ← crdtMerge(localOperation.data, serverData)
                RETURN {resolution: "merge", data: mergedData}
                
            ELSE IF CONFLICT_RESOLUTION_STRATEGY === "user_prompt" THEN
                RETURN {resolution: "prompt_user", 
                       localData: localOperation.data, 
                       serverData: serverData}
            END IF
        END
    END FUNCTION

    FUNCTION: handleOfflineOperation(operationType, data)
        // Optimistic UI updates
        updateLocalUI(data)
        
        // Store in local IndexedDB
        localResult ← localDB.store(operationType, data)
        
        // Queue for later sync
        operation ← {
            type: operationType,
            data: data,
            timestamp: getCurrentTimestamp(),
            syncStatus: "pending"
        }
        
        queueOperation(operation)
        
        // Show offline indicator
        showOfflineToast("Changes saved locally. Will sync when online.")
        
        RETURN localResult
    END FUNCTION

    FUNCTION: pullFromSupabase()
        IF detectNetworkStatus() === "offline" THEN
            RETURN useLocalData()
        END IF
        
        TRY
            lastSyncTime ← getLastSyncTimestamp()
            
            // Pull incremental changes
            changes ← supabase.query()
                .select("*")
                .greater("updated_at", lastSyncTime)
                .order("updated_at", "asc")
                .limit(SYNC_BATCH_SIZE)
            
            FOR EACH change IN changes DO
                localRecord ← localDB.get(change.id)
                
                IF localRecord EXISTS AND localRecord.updated_at > change.updated_at THEN
                    // Local is newer, queue for push
                    queueOperation({type: "update", data: localRecord})
                ELSE
                    // Server is newer, update local
                    localDB.upsert(change)
                END IF
            END FOR
            
            updateSyncTimestamp()
            RETURN "pull_complete"
            
        CATCH NetworkError e
            RETURN useLocalData()
        END TRY
    END FUNCTION

    EVENT_HANDLERS:
        // Network status changes
        addEventListener("online", () => {
            showOnlineToast("Back online. Syncing changes...")
            scheduleSync()
        })
        
        addEventListener("offline", () => {
            showOfflineToast("Working offline. Changes will sync when online.")
        })
        
        // Periodic sync when online
        setInterval(() => {
            IF detectNetworkStatus() === "online" THEN
                syncWithSupabase()
            END IF
        }, HEARTBEAT_INTERVAL)

END_ALGORITHM

COMPLEXITY_ANALYSIS:
    Time Complexity:
        - Queue operation: O(log n)
        - Sync batch: O(m * log m) where m = batch size
        - Conflict resolution: O(1) for last-write-wins, O(n) for CRDT
    
    Space Complexity:
        - Sync queue: O(n) where n = pending operations
        - Local cache: O(d) where d = data size
        
    Performance Optimizations:
        - Use web workers for sync operations
        - Implement binary exponential backoff for retries
        - Batch operations to reduce HTTP requests
        - Use IndexedDB transactions for atomicity
```

---

## 2. VOCABULARY EXTRACTION ALGORITHM

### Overview
Real-time vocabulary parsing from streaming GPT responses with duplicate detection, difficulty scoring, and spaced repetition integration.

```
ALGORITHM: VocabularyExtractionEngine
INPUT: streamingText (string), userLevel (enum), context (object)
OUTPUT: extractedVocabulary (array of VocabularyItem)

CONSTANTS:
    MIN_WORD_LENGTH = 3
    MAX_VOCABULARY_PER_RESPONSE = 15
    DIFFICULTY_LEVELS = ["beginner", "intermediate", "advanced", "native"]
    EXTRACTION_DEBOUNCE_MS = 500

DATA STRUCTURES:
    VocabularyItem:
        - word: string
        - translation: string
        - difficulty: number (1-10)
        - frequency: number
        - context: string
        - partOfSpeech: enum
        - spamcedRepetition: {nextReview: date, easiness: number}
    
    StreamBuffer:
        - content: string
        - position: number
        - pendingChunks: array
    
    DifficultyScorer:
        - frequencyTable: Map<string, number>
        - complexityRules: array

BEGIN_ALGORITHM: VocabularyExtractionEngine

    INITIALIZATION:
        streamBuffer ← StreamBuffer()
        difficultyScorer ← DifficultyScorer()
        extractedCache ← Map()
        userProfile ← getUserLearningProfile()
        debouncedExtract ← debounce(extractVocabulary, EXTRACTION_DEBOUNCE_MS)

    FUNCTION: processStreamingChunk(chunk)
        BEGIN
            // Add chunk to buffer
            streamBuffer.content ← streamBuffer.content + chunk
            streamBuffer.pendingChunks.push(chunk)
            
            // Real-time UI update
            updateStreamingUI(chunk)
            
            // Debounced vocabulary extraction
            debouncedExtract(streamBuffer.content)
        END
    END FUNCTION

    FUNCTION: extractVocabulary(text)
        BEGIN
            // Tokenize and clean text
            tokens ← tokenizeSpanishText(text)
            candidateWords ← filterCandidates(tokens)
            
            vocabularyItems ← []
            
            FOR EACH word IN candidateWords DO
                IF NOT isAlreadyKnown(word) AND NOT isDuplicate(word) THEN
                    vocabularyItem ← analyzeWord(word, text)
                    
                    IF vocabularyItem.difficulty <= getDifficultyThreshold(userProfile.level) THEN
                        vocabularyItems.append(vocabularyItem)
                    END IF
                END IF
            END FOR
            
            // Sort by learning value (difficulty vs usefulness)
            vocabularyItems ← sortByLearningValue(vocabularyItems)
            
            // Limit to max items
            finalVocabulary ← vocabularyItems.slice(0, MAX_VOCABULARY_PER_RESPONSE)
            
            // Update UI with extracted vocabulary
            updateVocabularyUI(finalVocabulary)
            
            RETURN finalVocabulary
        END
    END FUNCTION

    FUNCTION: analyzeWord(word, context)
        BEGIN
            // Get base translation
            translation ← getTranslation(word, context)
            
            // Calculate difficulty score
            difficulty ← calculateDifficulty(word, context)
            
            // Determine part of speech
            partOfSpeech ← analyzePOS(word, context)
            
            // Calculate frequency score
            frequency ← getWordFrequency(word)
            
            // Extract surrounding context
            wordContext ← extractContext(word, context, 50)  // 50 chars around
            
            vocabularyItem ← VocabularyItem{
                word: word,
                translation: translation,
                difficulty: difficulty,
                frequency: frequency,
                context: wordContext,
                partOfSpeech: partOfSpeech,
                spacedRepetition: initializeSpacedRepetition(difficulty)
            }
            
            RETURN vocabularyItem
        END
    END FUNCTION

    FUNCTION: calculateDifficulty(word, context)
        BEGIN
            difficultyScore ← 1.0  // Base difficulty
            
            // Length-based difficulty
            IF word.length > 8 THEN
                difficultyScore ← difficultyScore + 1.5
            ELSE IF word.length > 12 THEN
                difficultyScore ← difficultyScore + 2.5
            END IF
            
            // Morphological complexity
            IF hasComplexConjugation(word) THEN
                difficultyScore ← difficultyScore + 1.0
            END IF
            
            // Frequency in common Spanish (inverse relationship)
            commonFreq ← getCommonSpanishFrequency(word)
            IF commonFreq < 0.001 THEN  // Very rare word
                difficultyScore ← difficultyScore + 2.0
            ELSE IF commonFreq > 0.1 THEN  // Very common word
                difficultyScore ← difficultyScore - 0.5
            END IF
            
            // Context-based difficulty
            IF isIdiomaticExpression(word, context) THEN
                difficultyScore ← difficultyScore + 1.5
            END IF
            
            IF isTechnicalTerm(word, context) THEN
                difficultyScore ← difficultyScore + 1.0
            END IF
            
            // Cognate bonus (easier for English speakers)
            IF isCognate(word, "english") THEN
                difficultyScore ← difficultyScore - 1.0
            END IF
            
            // Normalize to 1-10 scale
            difficultyScore ← Math.max(1, Math.min(10, difficultyScore))
            
            RETURN difficultyScore
        END
    END FUNCTION

    FUNCTION: isAlreadyKnown(word)
        BEGIN
            // Check user's vocabulary database
            userVocab ← getUserVocabulary()
            
            IF userVocab.contains(word) THEN
                // Check if word is mastered
                wordStats ← userVocab.get(word)
                IF wordStats.masteryLevel > 0.8 THEN
                    RETURN true
                END IF
            END IF
            
            // Check against common word lists
            IF isInCommonWordList(word, userProfile.level) THEN
                RETURN true
            END IF
            
            RETURN false
        END
    END FUNCTION

    FUNCTION: isDuplicate(word)
        BEGIN
            // Check current session cache
            IF extractedCache.has(word) THEN
                RETURN true
            END IF
            
            // Check for lemma duplicates (different conjugations)
            lemma ← getLemma(word)
            FOR EACH cachedWord IN extractedCache.keys() DO
                IF getLemma(cachedWord) === lemma THEN
                    RETURN true
                END IF
            END FOR
            
            RETURN false
        END
    END FUNCTION

    FUNCTION: getTranslation(word, context)
        BEGIN
            // Try context-aware translation first
            contextTranslation ← getContextualTranslation(word, context)
            IF contextTranslation.confidence > 0.8 THEN
                RETURN contextTranslation.translation
            END IF
            
            // Fallback to dictionary lookup
            dictionaryTranslation ← getDictionaryTranslation(word)
            RETURN dictionaryTranslation
        END
    END FUNCTION

    FUNCTION: sortByLearningValue(vocabularyItems)
        BEGIN
            SORT vocabularyItems BY (item) => {
                // Higher learning value = better for user
                learningValue ← 0
                
                // Difficulty sweet spot (not too easy, not too hard)
                idealDifficulty ← getDifficultyIdeal(userProfile.level)
                difficultyPenalty ← Math.abs(item.difficulty - idealDifficulty)
                learningValue ← learningValue - difficultyPenalty
                
                // Frequency bonus (more useful words first)
                learningValue ← learningValue + (item.frequency * 2)
                
                // Recency bonus (words from current context)
                IF isFromCurrentContext(item) THEN
                    learningValue ← learningValue + 3
                END IF
                
                RETURN learningValue
            }
            
            RETURN vocabularyItems
        END
    END FUNCTION

    ASYNC FUNCTION: enhanceWithAI(vocabularyItems)
        BEGIN
            // Batch enhance vocabulary with GPT for better translations
            enhancedItems ← []
            
            FOR EACH batch IN batchItems(vocabularyItems, 5) DO
                prompt ← buildEnhancementPrompt(batch)
                
                aiResponse ← await callGPT({
                    prompt: prompt,
                    maxTokens: 300,
                    temperature: 0.3
                })
                
                enhancements ← parseAIEnhancements(aiResponse)
                enhancedItems.concat(applyEnhancements(batch, enhancements))
            END FOR
            
            RETURN enhancedItems
        END
    END FUNCTION

    // Real-time streaming integration
    STREAM_HANDLER: onGPTStream
        BEGIN
            chunk ← event.data
            processStreamingChunk(chunk)
            
            // Update progress indicator
            updateExtractionProgress(streamBuffer.content.length)
        END

END_ALGORITHM

COMPLEXITY_ANALYSIS:
    Time Complexity:
        - Stream processing: O(1) per chunk
        - Vocabulary extraction: O(n * log n) where n = word count
        - Difficulty calculation: O(1) per word
        - Duplicate detection: O(m) where m = cached words
    
    Space Complexity:
        - Stream buffer: O(k) where k = buffer size
        - Vocabulary cache: O(v) where v = vocabulary items
        
    Performance Optimizations:
        - Debounced extraction to avoid excessive processing
        - Web Worker for heavy linguistic analysis
        - IndexedDB caching for translations and difficulty scores
        - Streaming updates for real-time UI feedback
```

---

## 3. IMAGE SEARCH WITH CACHING ALGORITHM

### Overview
Efficient image search with intelligent caching, progressive loading, and bandwidth-aware quality selection.

```
ALGORITHM: ImageSearchCacheManager
INPUT: query (string), options (object)
OUTPUT: searchResults (array of ImageResult)

CONSTANTS:
    CACHE_SIZE_LIMIT = 100 * 1024 * 1024  // 100MB
    MAX_CONCURRENT_DOWNLOADS = 4
    QUALITY_LEVELS = ["thumb", "small", "regular", "full"]
    PRELOAD_THRESHOLD = 3  // Images to preload ahead
    CACHE_EXPIRY_HOURS = 24

DATA STRUCTURES:
    ImageCache: LRU Cache
        - entries: Map<url, CacheEntry>
        - size: number
        - maxSize: number
    
    CacheEntry:
        - url: string
        - blob: Blob
        - metadata: object
        - lastAccessed: timestamp
        - sizeBytes: number
        - quality: enum
    
    SearchState:
        - query: string
        - page: number
        - totalPages: number
        - results: array
        - loading: boolean
        - hasMore: boolean

BEGIN_ALGORITHM: ImageSearchCacheManager

    INITIALIZATION:
        imageCache ← LRUCache(CACHE_SIZE_LIMIT)
        downloadQueue ← PriorityQueue()
        searchHistory ← Map()
        bandwidthMonitor ← BandwidthMonitor()
        progressiveLoader ← ProgressiveLoader()

    FUNCTION: searchImages(query, page = 1, options = {})
        BEGIN
            searchKey ← generateSearchKey(query, page, options)
            
            // Check cache first
            cachedResults ← searchHistory.get(searchKey)
            IF cachedResults AND NOT isExpired(cachedResults) THEN
                displayCachedResults(cachedResults)
                preloadNextImages(cachedResults, page)
                RETURN cachedResults
            END IF
            
            // Show loading state
            updateSearchState({loading: true, query: query})
            
            TRY
                // API call with retry logic
                apiResults ← await searchUnsplash(query, page, options)
                
                // Process and enhance results
                processedResults ← await processSearchResults(apiResults)
                
                // Cache search results
                cacheSearchResults(searchKey, processedResults)
                
                // Update search state
                updateSearchState({
                    results: processedResults,
                    loading: false,
                    hasMore: apiResults.hasMore,
                    totalPages: apiResults.totalPages
                })
                
                // Start progressive loading
                startProgressiveLoading(processedResults)
                
                RETURN processedResults
                
            CATCH error
                handleSearchError(error)
                RETURN fallbackToCache(query) || []
            END TRY
        END
    END FUNCTION

    FUNCTION: processSearchResults(apiResults)
        BEGIN
            processedResults ← []
            
            FOR EACH image IN apiResults.results DO
                // Determine optimal quality based on bandwidth
                optimalQuality ← selectOptimalQuality(image)
                
                imageResult ← {
                    id: image.id,
                    urls: image.urls,
                    description: image.description,
                    metadata: extractMetadata(image),
                    optimalQuality: optimalQuality,
                    cached: isImageCached(image.urls[optimalQuality]),
                    loading: false,
                    error: null
                }
                
                processedResults.append(imageResult)
            END FOR
            
            RETURN processedResults
        END
    END FUNCTION

    FUNCTION: selectOptimalQuality(image)
        BEGIN
            currentBandwidth ← bandwidthMonitor.getCurrentBandwidth()
            devicePixelRatio ← window.devicePixelRatio || 1
            viewportSize ← getViewportSize()
            
            // Bandwidth-based selection
            IF currentBandwidth < 1  // Slow connection (< 1 Mbps)
                RETURN "thumb"
            ELSE IF currentBandwidth < 5  // Medium connection (1-5 Mbps)
                RETURN "small"
            ELSE IF currentBandwidth < 20  // Fast connection (5-20 Mbps)
                RETURN "regular"
            ELSE  // Very fast connection (> 20 Mbps)
                RETURN "full"
            END IF
            
            // Device capability adjustment
            IF devicePixelRatio > 2 AND viewportSize.width > 1024 THEN
                // High DPI display, upgrade quality
                quality ← upgradeQuality(quality)
            END IF
            
            RETURN quality
        END
    END FUNCTION

    FUNCTION: startProgressiveLoading(results)
        BEGIN
            // Load visible images first
            visibleImages ← getVisibleImages(results)
            
            FOR EACH image IN visibleImages DO
                loadImageWithFallback(image, HIGH_PRIORITY)
            END FOR
            
            // Preload next batch
            nextBatch ← results.slice(visibleImages.length, 
                                    visibleImages.length + PRELOAD_THRESHOLD)
            
            FOR EACH image IN nextBatch DO
                loadImageWithFallback(image, LOW_PRIORITY)
            END FOR
        END
    END FUNCTION

    ASYNC FUNCTION: loadImageWithFallback(imageResult, priority)
        BEGIN
            cacheKey ← imageResult.urls[imageResult.optimalQuality]
            
            // Check cache first
            cachedImage ← imageCache.get(cacheKey)
            IF cachedImage THEN
                displayImage(imageResult.id, cachedImage.blob)
                RETURN cachedImage
            END IF
            
            // Update loading state
            updateImageState(imageResult.id, {loading: true})
            
            // Add to download queue
            downloadRequest ← {
                id: imageResult.id,
                url: cacheKey,
                priority: priority,
                quality: imageResult.optimalQuality,
                fallbackUrls: generateFallbackUrls(imageResult)
            }
            
            downloadQueue.enqueue(downloadRequest, priority)
            processDownloadQueue()
        END
    END FUNCTION

    ASYNC FUNCTION: processDownloadQueue()
        BEGIN
            // Limit concurrent downloads
            activeDownloads ← getActiveDownloads()
            IF activeDownloads.length >= MAX_CONCURRENT_DOWNLOADS THEN
                RETURN
            END IF
            
            WHILE NOT downloadQueue.isEmpty() AND 
                  activeDownloads.length < MAX_CONCURRENT_DOWNLOADS DO
                
                request ← downloadQueue.dequeue()
                downloadImage(request)
            END WHILE
        END
    END FUNCTION

    ASYNC FUNCTION: downloadImage(request)
        BEGIN
            TRY
                // Progressive enhancement: start with lower quality
                IF request.quality !== "thumb" THEN
                    thumbUrl ← getThumbUrl(request.url)
                    IF NOT imageCache.has(thumbUrl) THEN
                        thumbBlob ← await fetchImageBlob(thumbUrl)
                        cacheImage(thumbUrl, thumbBlob, "thumb")
                        displayPlaceholder(request.id, thumbBlob)
                    END IF
                END IF
                
                // Download target quality
                imageBlob ← await fetchImageBlob(request.url)
                
                // Cache the image
                cacheImage(request.url, imageBlob, request.quality)
                
                // Display final image
                displayImage(request.id, imageBlob)
                updateImageState(request.id, {loading: false, cached: true})
                
            CATCH error
                // Try fallback URLs
                FOR EACH fallbackUrl IN request.fallbackUrls DO
                    TRY
                        fallbackBlob ← await fetchImageBlob(fallbackUrl)
                        cacheImage(fallbackUrl, fallbackBlob, "fallback")
                        displayImage(request.id, fallbackBlob)
                        RETURN
                    CATCH fallbackError
                        CONTINUE
                    END TRY
                END FOR
                
                // All failed, show error state
                updateImageState(request.id, {loading: false, error: error})
                displayImageError(request.id, error)
            END TRY
        END
    END FUNCTION

    FUNCTION: cacheImage(url, blob, quality)
        BEGIN
            entry ← CacheEntry{
                url: url,
                blob: blob,
                quality: quality,
                sizeBytes: blob.size,
                lastAccessed: getCurrentTimestamp(),
                metadata: {
                    width: blob.width,
                    height: blob.height,
                    format: blob.type
                }
            }
            
            // Check cache size limit
            WHILE imageCache.size + entry.sizeBytes > CACHE_SIZE_LIMIT DO
                evictLRUEntry()
            END WHILE
            
            imageCache.set(url, entry)
            
            // Update cache statistics
            updateCacheStats()
        END
    END FUNCTION

    FUNCTION: evictLRUEntry()
        BEGIN
            oldestEntry ← imageCache.getLRU()
            IF oldestEntry THEN
                imageCache.delete(oldestEntry.url)
                
                // Clean up blob URL if created
                IF oldestEntry.blobUrl THEN
                    URL.revokeObjectURL(oldestEntry.blobUrl)
                END IF
            END IF
        END
    END FUNCTION

    FUNCTION: preloadNextImages(currentResults, currentPage)
        BEGIN
            // Preload next page if near end
            IF shouldPreloadNextPage(currentResults, currentPage) THEN
                nextPageResults ← await searchImages(
                    currentResults.query, 
                    currentPage + 1, 
                    {preload: true}
                )
                
                // Cache but don't display
                FOR EACH image IN nextPageResults.slice(0, 3) DO
                    loadImageWithFallback(image, LOW_PRIORITY)
                END FOR
            END IF
        END
    END FUNCTION

    // Intersection Observer for lazy loading
    INTERSECTION_OBSERVER: imageVisibilityObserver
        BEGIN
            FOR EACH entry IN entries DO
                IF entry.isIntersecting THEN
                    imageElement ← entry.target
                    imageId ← imageElement.dataset.imageId
                    
                    // Load image if not already loaded
                    IF NOT isImageLoaded(imageId) THEN
                        loadImageWithFallback(getImageResult(imageId), MEDIUM_PRIORITY)
                    END IF
                    
                    // Stop observing once loaded
                    imageVisibilityObserver.unobserve(imageElement)
                END IF
            END FOR
        END

    // Bandwidth monitoring
    BANDWIDTH_MONITOR: bandwidthMonitor
        BEGIN
            samples ← []
            
            FUNCTION: measureBandwidth()
                startTime ← performance.now()
                testImage ← new Image()
                
                testImage.onload ← () => {
                    endTime ← performance.now()
                    duration ← endTime - startTime
                    bandwidth ← calculateBandwidth(TEST_IMAGE_SIZE, duration)
                    samples.push(bandwidth)
                    
                    // Keep rolling average of last 5 samples
                    IF samples.length > 5 THEN
                        samples.shift()
                    END IF
                }
                
                testImage.src ← TEST_IMAGE_URL + "?t=" + Date.now()
            END FUNCTION
            
            // Measure bandwidth periodically
            setInterval(measureBandwidth, 30000)  // Every 30 seconds
        END

END_ALGORITHM

COMPLEXITY_ANALYSIS:
    Time Complexity:
        - Search: O(1) for cached, O(n) for API call
        - Image loading: O(k) where k = concurrent downloads
        - Cache operations: O(1) for LRU cache
        - Quality selection: O(1)
    
    Space Complexity:
        - Image cache: O(CACHE_SIZE_LIMIT) bounded
        - Search cache: O(s) where s = search history size
        - Download queue: O(q) where q = queued requests
    
    Performance Optimizations:
        - Lazy loading with Intersection Observer
        - Progressive image enhancement (thumb → full)
        - Bandwidth-aware quality selection
        - LRU cache with size limits
        - Concurrent download limiting
        - Preloading for smoother navigation
```

---

## 4. QUIZ GENERATION ALGORITHM

### Overview
Adaptive quiz generation with difficulty adjustment, question type variety, and spaced repetition integration.

```
ALGORITHM: AdaptiveQuizGenerator
INPUT: vocabularyPool (array), userProfile (object), preferences (object)
OUTPUT: quizSession (QuizSession)

CONSTANTS:
    MIN_QUIZ_LENGTH = 5
    MAX_QUIZ_LENGTH = 20
    DEFAULT_QUIZ_LENGTH = 10
    QUESTION_TYPES = ["translation", "multiple_choice", "fill_blank", "audio"]
    DIFFICULTY_ADJUSTMENT_FACTOR = 0.1
    SPACED_REPETITION_WEIGHTS = {due: 3.0, overdue: 5.0, new: 1.0}

DATA STRUCTURES:
    QuizSession:
        - id: string
        - questions: array<Question>
        - currentIndex: number
        - startTime: timestamp
        - userAnswers: array
        - adaptiveState: AdaptiveState
    
    Question:
        - id: string
        - type: enum
        - vocabulary: VocabularyItem
        - prompt: string
        - options: array (for multiple choice)
        - correctAnswer: string
        - difficulty: number
        - timeLimit: number
    
    AdaptiveState:
        - currentDifficulty: number
        - streakCount: number
        - recentAccuracy: array
        - adjustmentHistory: array

BEGIN_ALGORITHM: AdaptiveQuizGenerator

    INITIALIZATION:
        questionGenerators ← Map<questionType, Generator>
        difficultyAdjuster ← DifficultyAdjuster()
        spacedRepetitionManager ← SpacedRepetitionManager()
        analyticsTracker ← AnalyticsTracker()

    FUNCTION: generateQuiz(vocabularyPool, userProfile, preferences)
        BEGIN
            // Determine quiz parameters
            quizLength ← determineQuizLength(preferences, userProfile)
            targetDifficulty ← calculateTargetDifficulty(userProfile)
            questionTypes ← selectQuestionTypes(preferences, userProfile.capabilities)
            
            // Select vocabulary based on spaced repetition and difficulty
            selectedVocab ← selectVocabularyForQuiz(vocabularyPool, quizLength, targetDifficulty)
            
            // Generate questions
            questions ← []
            adaptiveState ← initializeAdaptiveState(userProfile, targetDifficulty)
            
            FOR i ← 0 TO quizLength - 1 DO
                vocab ← selectedVocab[i]
                questionType ← selectQuestionType(questionTypes, i, adaptiveState)
                
                question ← generateQuestion(vocab, questionType, adaptiveState)
                questions.append(question)
                
                // Adjust difficulty for next question based on current trajectory
                adaptiveState ← adjustDifficultyForNext(adaptiveState, question)
            END FOR
            
            // Create quiz session
            quizSession ← QuizSession{
                id: generateQuizId(),
                questions: questions,
                currentIndex: 0,
                startTime: getCurrentTimestamp(),
                userAnswers: [],
                adaptiveState: adaptiveState,
                analytics: initializeAnalytics()
            }
            
            RETURN quizSession
        END
    END FUNCTION

    FUNCTION: selectVocabularyForQuiz(vocabularyPool, quizLength, targetDifficulty)
        BEGIN
            // Categorize vocabulary by spaced repetition status
            dueForReview ← filterDueForReview(vocabularyPool)
            overdueItems ← filterOverdue(vocabularyPool)
            newItems ← filterNew(vocabularyPool)
            
            // Calculate distribution based on spaced repetition principles
            distribution ← calculateDistribution(dueForReview, overdueItems, newItems, quizLength)
            
            selectedVocab ← []
            
            // Select overdue items first (highest priority)
            overdueSelected ← selectByDifficulty(overdueItems, distribution.overdue, targetDifficulty)
            selectedVocab.concat(overdueSelected)
            
            // Select due items
            dueSelected ← selectByDifficulty(dueForReview, distribution.due, targetDifficulty)
            selectedVocab.concat(dueSelected)
            
            // Fill remaining slots with new items
            remaining ← quizLength - selectedVocab.length
            IF remaining > 0 THEN
                newSelected ← selectByDifficulty(newItems, remaining, targetDifficulty)
                selectedVocab.concat(newSelected)
            END IF
            
            // Shuffle to avoid predictable patterns
            shuffleArray(selectedVocab)
            
            RETURN selectedVocab
        END
    END FUNCTION

    FUNCTION: selectByDifficulty(vocabularyItems, count, targetDifficulty)
        BEGIN
            // Score each item by its suitability for target difficulty
            scoredItems ← []
            
            FOR EACH item IN vocabularyItems DO
                difficultyMatch ← calculateDifficultyMatch(item.difficulty, targetDifficulty)
                urgencyScore ← calculateUrgencyScore(item)
                learningValue ← calculateLearningValue(item)
                
                totalScore ← difficultyMatch * 0.4 + urgencyScore * 0.4 + learningValue * 0.2
                
                scoredItems.append({item: item, score: totalScore})
            END FOR
            
            // Sort by score and take top items
            scoredItems.sortByDescending(score)
            selected ← scoredItems.slice(0, count).map(entry => entry.item)
            
            RETURN selected
        END
    END FUNCTION

    FUNCTION: generateQuestion(vocabulary, questionType, adaptiveState)
        BEGIN
            generator ← questionGenerators.get(questionType)
            
            baseQuestion ← generator.generate(vocabulary)
            
            // Adjust difficulty based on adaptive state
            adjustedQuestion ← adjustQuestionDifficulty(baseQuestion, adaptiveState)
            
            // Add time limit based on difficulty and question type
            timeLimit ← calculateTimeLimit(adjustedQuestion, questionType)
            
            question ← Question{
                id: generateQuestionId(),
                type: questionType,
                vocabulary: vocabulary,
                prompt: adjustedQuestion.prompt,
                options: adjustedQuestion.options,
                correctAnswer: adjustedQuestion.correctAnswer,
                difficulty: adjustedQuestion.difficulty,
                timeLimit: timeLimit,
                metadata: {
                    generatedAt: getCurrentTimestamp(),
                    adaptiveLevel: adaptiveState.currentDifficulty
                }
            }
            
            RETURN question
        END
    END FUNCTION

    // Specific question generators
    QUESTION_GENERATOR: translationGenerator
        FUNCTION: generate(vocabulary)
            // Simple translation question
            prompt ← `What does "${vocabulary.word}" mean in English?`
            correctAnswer ← vocabulary.translation
            
            RETURN {
                prompt: prompt,
                correctAnswer: correctAnswer,
                options: null,
                difficulty: vocabulary.difficulty
            }
        END
    
    QUESTION_GENERATOR: multipleChoiceGenerator
        FUNCTION: generate(vocabulary)
            prompt ← `What does "${vocabulary.word}" mean?`
            correctAnswer ← vocabulary.translation
            
            // Generate distractors
            distractors ← generateDistractors(vocabulary, 3)
            options ← shuffleArray([correctAnswer, ...distractors])
            
            RETURN {
                prompt: prompt,
                correctAnswer: correctAnswer,
                options: options,
                difficulty: vocabulary.difficulty - 0.5  // Slightly easier due to options
            }
        END

    QUESTION_GENERATOR: fillBlankGenerator
        FUNCTION: generate(vocabulary)
            // Use context sentence with blank
            contextSentence ← vocabulary.context || generateContextSentence(vocabulary)
            blankedSentence ← contextSentence.replace(vocabulary.word, "______")
            
            prompt ← `Fill in the blank: ${blankedSentence}`
            correctAnswer ← vocabulary.word
            
            RETURN {
                prompt: prompt,
                correctAnswer: correctAnswer,
                options: null,
                difficulty: vocabulary.difficulty + 0.5  // Harder due to context
            }
        END

    FUNCTION: processAnswer(quizSession, questionIndex, userAnswer, timeSpent)
        BEGIN
            question ← quizSession.questions[questionIndex]
            isCorrect ← evaluateAnswer(question, userAnswer)
            
            // Record answer
            answerRecord ← {
                questionId: question.id,
                userAnswer: userAnswer,
                correctAnswer: question.correctAnswer,
                isCorrect: isCorrect,
                timeSpent: timeSpent,
                timestamp: getCurrentTimestamp()
            }
            
            quizSession.userAnswers.append(answerRecord)
            
            // Update adaptive state
            quizSession.adaptiveState ← updateAdaptiveState(
                quizSession.adaptiveState, 
                isCorrect, 
                timeSpent, 
                question.difficulty
            )
            
            // Update spaced repetition for vocabulary item
            spacedRepetitionManager.updateItem(question.vocabulary.id, isCorrect, timeSpent)
            
            // Track analytics
            analyticsTracker.recordAnswer(answerRecord, question)
            
            // Generate real-time feedback
            feedback ← generateFeedback(answerRecord, question)
            
            RETURN {
                isCorrect: isCorrect,
                feedback: feedback,
                adaptiveUpdate: quizSession.adaptiveState
            }
        END
    END FUNCTION

    FUNCTION: updateAdaptiveState(adaptiveState, isCorrect, timeSpent, questionDifficulty)
        BEGIN
            // Update streak
            IF isCorrect THEN
                adaptiveState.streakCount ← adaptiveState.streakCount + 1
            ELSE
                adaptiveState.streakCount ← 0
            END IF
            
            // Update recent accuracy (rolling window of last 5 answers)
            adaptiveState.recentAccuracy.append(isCorrect ? 1 : 0)
            IF adaptiveState.recentAccuracy.length > 5 THEN
                adaptiveState.recentAccuracy.shift()
            END IF
            
            // Calculate current accuracy
            currentAccuracy ← adaptiveState.recentAccuracy.reduce(sum) / adaptiveState.recentAccuracy.length
            
            // Adjust difficulty based on performance
            difficultyAdjustment ← 0
            
            IF currentAccuracy > 0.8 THEN
                // User is doing well, increase difficulty
                difficultyAdjustment ← DIFFICULTY_ADJUSTMENT_FACTOR
            ELSE IF currentAccuracy < 0.4 THEN
                // User is struggling, decrease difficulty
                difficultyAdjustment ← -DIFFICULTY_ADJUSTMENT_FACTOR
            END IF
            
            // Factor in time performance
            expectedTime ← calculateExpectedTime(questionDifficulty)
            IF timeSpent < expectedTime * 0.7 THEN
                // Very fast, might be too easy
                difficultyAdjustment ← difficultyAdjustment + (DIFFICULTY_ADJUSTMENT_FACTOR * 0.5)
            ELSE IF timeSpent > expectedTime * 1.5 THEN
                // Very slow, might be too hard
                difficultyAdjustment ← difficultyAdjustment - (DIFFICULTY_ADJUSTMENT_FACTOR * 0.5)
            END IF
            
            // Apply adjustment with bounds
            adaptiveState.currentDifficulty ← Math.max(1, 
                Math.min(10, adaptiveState.currentDifficulty + difficultyAdjustment))
            
            // Record adjustment for analytics
            adaptiveState.adjustmentHistory.append({
                timestamp: getCurrentTimestamp(),
                adjustment: difficultyAdjustment,
                accuracy: currentAccuracy,
                streak: adaptiveState.streakCount
            })
            
            RETURN adaptiveState
        END
    END FUNCTION

    FUNCTION: generateFeedback(answerRecord, question)
        BEGIN
            feedback ← {
                message: "",
                type: answerRecord.isCorrect ? "success" : "error",
                explanation: "",
                tips: []
            }
            
            IF answerRecord.isCorrect THEN
                IF answerRecord.timeSpent < calculateExpectedTime(question.difficulty) * 0.8 THEN
                    feedback.message ← "Excellent! Quick and correct! 🎉"
                ELSE
                    feedback.message ← "Correct! Well done! ✅"
                END IF
                
                // Add contextual information for correct answers
                IF question.vocabulary.etymology THEN
                    feedback.explanation ← `Etymology: ${question.vocabulary.etymology}`
                END IF
                
            ELSE
                feedback.message ← "Not quite right. Keep learning! 💪"
                feedback.explanation ← `The correct answer is: ${question.correctAnswer}`
                
                // Add learning tips for incorrect answers
                feedback.tips ← generateLearningTips(question.vocabulary, answerRecord.userAnswer)
            END IF
            
            RETURN feedback
        END
    END FUNCTION

    FUNCTION: completeQuiz(quizSession)
        BEGIN
            endTime ← getCurrentTimestamp()
            totalTime ← endTime - quizSession.startTime
            
            // Calculate final statistics
            correctAnswers ← quizSession.userAnswers.filter(answer => answer.isCorrect).length
            accuracy ← correctAnswers / quizSession.questions.length
            avgTimePerQuestion ← totalTime / quizSession.questions.length
            
            // Generate performance analysis
            analysis ← analyzeQuizPerformance(quizSession)
            
            // Update user profile based on performance
            updateUserProfile(quizSession, analysis)
            
            // Generate recommendations
            recommendations ← generateRecommendations(analysis)
            
            results ← {
                score: correctAnswers,
                totalQuestions: quizSession.questions.length,
                accuracy: accuracy,
                totalTime: totalTime,
                avgTimePerQuestion: avgTimePerQuestion,
                analysis: analysis,
                recommendations: recommendations,
                improvementAreas: identifyImprovementAreas(quizSession)
            }
            
            // Save results for spaced repetition
            saveQuizResults(quizSession, results)
            
            RETURN results
        END
    END FUNCTION

    // Real-time multiplayer support
    MULTIPLAYER_HANDLER: multiplayerQuizManager
        FUNCTION: createMultiplayerSession(hostUser, settings)
            sessionId ← generateSessionId()
            
            session ← {
                id: sessionId,
                host: hostUser,
                participants: [hostUser],
                settings: settings,
                state: "waiting",
                quiz: null,
                realTimeScores: Map()
            }
            
            // Broadcast session creation
            broadcastToChannel("quiz_sessions", {
                type: "session_created",
                session: session
            })
            
            RETURN session
        END
        
        FUNCTION: syncMultiplayerAnswers(sessionId, userId, answer)
            session ← getMultiplayerSession(sessionId)
            
            // Record answer with timestamp
            answerData ← {
                userId: userId,
                answer: answer,
                timestamp: getCurrentTimestamp()
            }
            
            // Broadcast to all participants
            broadcastToSession(sessionId, {
                type: "participant_answered",
                data: answerData
            })
            
            // Update real-time leaderboard
            updateRealtimeLeaderboard(sessionId, userId, answer.isCorrect)
        END

END_ALGORITHM

COMPLEXITY_ANALYSIS:
    Time Complexity:
        - Quiz generation: O(n log n) where n = vocabulary pool size
        - Question generation: O(1) per question
        - Answer processing: O(1) per answer
        - Adaptive adjustment: O(1)
        - Multiplayer sync: O(p) where p = participants
    
    Space Complexity:
        - Quiz session: O(q) where q = number of questions
        - Adaptive state: O(h) where h = history length
        - Multiplayer sessions: O(s * p) where s = sessions, p = participants
    
    Performance Optimizations:
        - Pregenerate question pools for common vocabulary
        - Use Web Workers for complex question generation
        - Cache distractor options for multiple choice
        - Real-time sync with debouncing for multiplayer
        - Progressive quiz loading for long sessions
```

---

## 5. AI STREAMING RESPONSE HANDLER

### Overview
Efficient handling of streaming GPT responses with chunk assembly, error recovery, and real-time UI updates.

```
ALGORITHM: AIStreamingResponseHandler
INPUT: streamEndpoint (string), requestPayload (object), options (object)
OUTPUT: StreamingResponse (stream)

CONSTANTS:
    MAX_CHUNK_SIZE = 8192
    RECONNECTION_ATTEMPTS = 3
    RECONNECTION_DELAY_MS = 1000
    HEARTBEAT_INTERVAL = 30000
    TOKEN_USAGE_TRACKING = true
    RESPONSE_CACHE_SIZE = 50

DATA STRUCTURES:
    StreamingResponse:
        - id: string
        - content: string
        - chunks: array
        - isComplete: boolean
        - error: Error | null
        - metadata: object
    
    ChunkProcessor:
        - buffer: string
        - pendingChunks: array
        - assembledContent: string
        - position: number
    
    ErrorRecovery:
        - retryCount: number
        - lastError: Error
        - backoffDelay: number
        - recoveryStrategies: array

BEGIN_ALGORITHM: AIStreamingResponseHandler

    INITIALIZATION:
        eventSourceManager ← EventSourceManager()
        chunkProcessor ← ChunkProcessor()
        errorRecovery ← ErrorRecovery()
        tokenTracker ← TokenUsageTracker()
        responseCache ← LRUCache(RESPONSE_CACHE_SIZE)
        metricsCollector ← MetricsCollector()

    ASYNC FUNCTION: initiateStream(endpoint, payload, options)
        BEGIN
            streamId ← generateStreamId()
            
            // Check cache for similar requests
            cacheKey ← generateCacheKey(payload)
            cachedResponse ← responseCache.get(cacheKey)
            IF cachedResponse AND options.allowCached THEN
                RETURN replayStreamFromCache(cachedResponse, streamId)
            END IF
            
            // Initialize streaming response
            streamingResponse ← StreamingResponse{
                id: streamId,
                content: "",
                chunks: [],
                isComplete: false,
                error: null,
                metadata: {
                    startTime: getCurrentTimestamp(),
                    endpoint: endpoint,
                    model: payload.model,
                    estimatedTokens: estimateTokenCount(payload),
                    actualTokens: 0
                }
            }
            
            // Set up event source with error handling
            eventSource ← createEventSource(endpoint, payload, streamId)
            
            // Configure event handlers
            setupStreamEventHandlers(eventSource, streamingResponse)
            
            // Start heartbeat monitoring
            startHeartbeatMonitoring(streamId)
            
            RETURN streamingResponse
        END
    END FUNCTION

    FUNCTION: setupStreamEventHandlers(eventSource, streamingResponse)
        BEGIN
            // Data chunk received
            eventSource.onmessage ← (event) => {
                TRY
                    chunkData ← parseStreamChunk(event.data)
                    processChunk(streamingResponse, chunkData)
                    updateUIRealtimeDisplay(streamingResponse)
                    
                CATCH error
                    handleChunkError(streamingResponse, error)
                END TRY
            }
            
            // Stream opened successfully
            eventSource.onopen ← (event) => {
                resetErrorRecovery()
                updateConnectionStatus(streamingResponse.id, "connected")
                metricsCollector.recordStreamStart(streamingResponse.id)
            }
            
            // Stream error occurred
            eventSource.onerror ← (error) => {
                handleStreamError(streamingResponse, error)
            }
            
            // Custom events for token usage
            eventSource.addEventListener("token_usage", (event) => {
                tokenData ← JSON.parse(event.data)
                updateTokenUsage(streamingResponse, tokenData)
            })
            
            // Stream completion event
            eventSource.addEventListener("completion", (event) => {
                completeStream(streamingResponse, JSON.parse(event.data))
            })
        END
    END FUNCTION

    FUNCTION: processChunk(streamingResponse, chunkData)
        BEGIN
            // Add chunk to processing queue
            chunkProcessor.buffer ← chunkProcessor.buffer + chunkData.content
            
            // Process complete sentences or meaningful units
            processedContent ← extractCompletedUnits(chunkProcessor.buffer)
            
            IF processedContent.length > 0 THEN
                // Update response content
                streamingResponse.content ← streamingResponse.content + processedContent
                
                // Store chunk metadata
                chunkMetadata ← {
                    sequence: streamingResponse.chunks.length,
                    content: processedContent,
                    timestamp: getCurrentTimestamp(),
                    size: processedContent.length,
                    processingDelay: chunkData.processingDelay || 0
                }
                
                streamingResponse.chunks.append(chunkMetadata)
                
                // Update buffer (remove processed content)
                chunkProcessor.buffer ← chunkProcessor.buffer.substring(processedContent.length)
                
                // Real-time vocabulary extraction
                IF options.extractVocabularyRealtime THEN
                    extractedVocab ← extractVocabularyFromChunk(processedContent)
                    updateVocabularyDisplay(extractedVocab)
                END IF
                
                // Update token count estimation
                estimatedTokens ← estimateTokenCount(processedContent)
                streamingResponse.metadata.actualTokens += estimatedTokens
                
                // Trigger real-time callbacks
                triggerChunkProcessedCallbacks(streamingResponse, processedContent)
            END IF
        END
    END FUNCTION

    FUNCTION: extractCompletedUnits(buffer)
        BEGIN
            completedUnits ← ""
            
            // Extract complete sentences (ending with ., !, ?, or \n)
            sentencePattern ← /^(.*?[.!?\n])/
            match ← buffer.match(sentencePattern)
            
            IF match THEN
                completedUnits ← match[1]
            ELSE
                // If no complete sentences, check for partial meaningful units
                // (at least 20 characters and ending with space or punctuation)
                IF buffer.length > 20 THEN
                    lastSpace ← buffer.lastIndexOf(' ')
                    IF lastSpace > 15 THEN  // Ensure meaningful chunk
                        completedUnits ← buffer.substring(0, lastSpace + 1)
                    END IF
                END IF
            END IF
            
            RETURN completedUnits
        END
    END FUNCTION

    FUNCTION: handleStreamError(streamingResponse, error)
        BEGIN
            errorRecovery.retryCount ← errorRecovery.retryCount + 1
            errorRecovery.lastError ← error
            
            metricsCollector.recordStreamError(streamingResponse.id, error)
            
            // Determine recovery strategy
            IF errorRecovery.retryCount <= RECONNECTION_ATTEMPTS THEN
                recoveryStrategy ← selectRecoveryStrategy(error)
                
                SWITCH recoveryStrategy
                    CASE "reconnect":
                        scheduleReconnection(streamingResponse)
                        
                    CASE "resume":
                        resumeStreamFromLastChunk(streamingResponse)
                        
                    CASE "fallback":
                        switchToFallbackEndpoint(streamingResponse)
                        
                    DEFAULT:
                        finalizeStreamWithError(streamingResponse, error)
                END SWITCH
            ELSE
                // Max retries exceeded
                finalizeStreamWithError(streamingResponse, error)
            END IF
        END
    END FUNCTION

    FUNCTION: selectRecoveryStrategy(error)
        BEGIN
            IF error.type === "network_error" THEN
                RETURN "reconnect"
            ELSE IF error.type === "timeout" THEN
                RETURN "resume"
            ELSE IF error.type === "server_error" AND error.status >= 500 THEN
                RETURN "fallback"
            ELSE IF error.type === "rate_limit" THEN
                RETURN "backoff_reconnect"
            ELSE
                RETURN "fail"
            END IF
        END
    END FUNCTION

    ASYNC FUNCTION: scheduleReconnection(streamingResponse)
        BEGIN
            // Calculate backoff delay (exponential backoff)
            backoffDelay ← RECONNECTION_DELAY_MS * Math.pow(2, errorRecovery.retryCount - 1)
            
            updateConnectionStatus(streamingResponse.id, "reconnecting", backoffDelay)
            
            await sleep(backoffDelay)
            
            // Attempt reconnection
            TRY
                newEventSource ← recreateEventSource(streamingResponse)
                
                // Resume from last successful position
                resumePayload ← createResumePayload(streamingResponse)
                
                setupStreamEventHandlers(newEventSource, streamingResponse)
                
            CATCH reconnectionError
                handleStreamError(streamingResponse, reconnectionError)
            END TRY
        END
    END FUNCTION

    FUNCTION: createResumePayload(streamingResponse)
        BEGIN
            // Create payload to resume from last successful chunk
            lastChunk ← streamingResponse.chunks[streamingResponse.chunks.length - 1]
            
            resumePayload ← {
                ...originalPayload,
                resumeFromPosition: lastChunk ? lastChunk.sequence : 0,
                partialContent: streamingResponse.content
            }
            
            RETURN resumePayload
        END
    END FUNCTION

    FUNCTION: completeStream(streamingResponse, completionData)
        BEGIN
            // Process any remaining buffer content
            IF chunkProcessor.buffer.trim().length > 0 THEN
                streamingResponse.content ← streamingResponse.content + chunkProcessor.buffer
                
                finalChunk ← {
                    sequence: streamingResponse.chunks.length,
                    content: chunkProcessor.buffer,
                    timestamp: getCurrentTimestamp(),
                    size: chunkProcessor.buffer.length,
                    isFinal: true
                }
                
                streamingResponse.chunks.append(finalChunk)
            END IF
            
            // Mark as complete
            streamingResponse.isComplete ← true
            streamingResponse.metadata.endTime ← getCurrentTimestamp()
            streamingResponse.metadata.totalDuration ← 
                streamingResponse.metadata.endTime - streamingResponse.metadata.startTime
            
            // Update final token usage
            IF completionData.tokenUsage THEN
                streamingResponse.metadata.actualTokens ← completionData.tokenUsage.total
                streamingResponse.metadata.promptTokens ← completionData.tokenUsage.prompt
                streamingResponse.metadata.completionTokens ← completionData.tokenUsage.completion
            END IF
            
            // Cache completed response
            cacheKey ← generateCacheKey(originalPayload)
            responseCache.set(cacheKey, {
                content: streamingResponse.content,
                metadata: streamingResponse.metadata,
                timestamp: getCurrentTimestamp()
            })
            
            // Final vocabulary extraction
            IF options.extractVocabularyOnComplete THEN
                finalVocabulary ← extractVocabularyFromText(streamingResponse.content)
                updateFinalVocabularyDisplay(finalVocabulary)
            END IF
            
            // Clean up resources
            stopHeartbeatMonitoring(streamingResponse.id)
            eventSource.close()
            
            // Trigger completion callbacks
            triggerCompletionCallbacks(streamingResponse)
            
            // Record metrics
            metricsCollector.recordStreamCompletion(streamingResponse)
        END
    END FUNCTION

    FUNCTION: updateUIRealtimeDisplay(streamingResponse)
        BEGIN
            // Throttled UI updates to prevent overwhelming the browser
            currentTime ← getCurrentTimestamp()
            
            IF currentTime - lastUIUpdate > UI_UPDATE_THROTTLE_MS THEN
                // Update streaming text display
                updateStreamingTextElement(streamingResponse.content)
                
                // Update progress indicators
                updateProgressIndicators(streamingResponse)
                
                // Update token usage display
                updateTokenUsageDisplay(streamingResponse.metadata.actualTokens)
                
                lastUIUpdate ← currentTime
            END IF
        END
    END FUNCTION

    FUNCTION: estimateTokenCount(text)
        BEGIN
            // Rough estimation: ~4 characters per token for most languages
            // More sophisticated tokenization could be done with tiktoken
            
            baseEstimate ← Math.ceil(text.length / 4)
            
            // Adjust for language complexity
            IF isComplexLanguage(text) THEN
                baseEstimate ← baseEstimate * 1.2
            END IF
            
            // Adjust for special tokens (punctuation, numbers)
            specialTokens ← countSpecialTokens(text)
            
            RETURN baseEstimate + specialTokens
        END
    END FUNCTION

    // Token usage tracking
    TOKEN_TRACKER: tokenTracker
        BEGIN
            dailyUsage ← 0
            monthlyUsage ← 0
            costTracking ← Map<model, cost>()
            
            FUNCTION: trackTokens(model, promptTokens, completionTokens)
                total ← promptTokens + completionTokens
                
                // Update daily/monthly counters
                dailyUsage ← dailyUsage + total
                monthlyUsage ← monthlyUsage + total
                
                // Calculate cost
                cost ← calculateTokenCost(model, promptTokens, completionTokens)
                costTracking.set(model, (costTracking.get(model) || 0) + cost)
                
                // Check usage limits
                checkUsageLimits(dailyUsage, monthlyUsage)
                
                // Store in local storage for persistence
                saveTokenUsageStats()
            END FUNCTION
            
            FUNCTION: checkUsageLimits(daily, monthly)
                IF daily > DAILY_TOKEN_LIMIT THEN
                    showTokenLimitWarning("daily", daily, DAILY_TOKEN_LIMIT)
                END IF
                
                IF monthly > MONTHLY_TOKEN_LIMIT THEN
                    showTokenLimitWarning("monthly", monthly, MONTHLY_TOKEN_LIMIT)
                END IF
            END FUNCTION
        END

    // Performance monitoring
    METRICS_COLLECTOR: metricsCollector
        BEGIN
            streamMetrics ← Map()
            
            FUNCTION: recordStreamStart(streamId)
                streamMetrics.set(streamId, {
                    startTime: performance.now(),
                    chunkCount: 0,
                    errorCount: 0,
                    reconnectionCount: 0
                })
            END FUNCTION
            
            FUNCTION: recordStreamCompletion(streamingResponse)
                metrics ← streamMetrics.get(streamingResponse.id)
                
                IF metrics THEN
                    metrics.endTime ← performance.now()
                    metrics.totalDuration ← metrics.endTime - metrics.startTime
                    metrics.avgChunkDelay ← calculateAvgChunkDelay(streamingResponse.chunks)
                    metrics.tokensPerSecond ← streamingResponse.metadata.actualTokens / 
                                             (metrics.totalDuration / 1000)
                    
                    // Store metrics for analytics
                    storePerformanceMetrics(streamingResponse.id, metrics)
                END IF
            END FUNCTION
        END

END_ALGORITHM

COMPLEXITY_ANALYSIS:
    Time Complexity:
        - Stream initialization: O(1)
        - Chunk processing: O(k) where k = chunk size
        - Error recovery: O(r) where r = retry attempts
        - UI updates: O(1) with throttling
        - Token counting: O(n) where n = text length
    
    Space Complexity:
        - Stream buffer: O(b) where b = buffer size
        - Chunk storage: O(c * s) where c = chunk count, s = chunk size
        - Cache: O(RESPONSE_CACHE_SIZE)
        - Metrics: O(m) where m = concurrent streams
    
    Performance Optimizations:
        - Throttled UI updates to prevent browser overload
        - Chunked processing for real-time feedback
        - Exponential backoff for retry logic
        - LRU caching for response reuse
        - Web Workers for heavy processing tasks
        - Progressive vocabulary extraction
```

---

## 6. COLLABORATIVE FEATURES ALGORITHM

### Overview
Real-time collaboration system with optimistic UI updates, conflict resolution, and presence indicators.

```
ALGORITHM: CollaborativeFeatureManager
INPUT: None (manages collaborative state)
OUTPUT: Real-time synchronized collaboration

CONSTANTS:
    PRESENCE_UPDATE_INTERVAL = 5000  // 5 seconds
    CONFLICT_RESOLUTION_TIMEOUT = 10000  // 10 seconds
    MAX_CONCURRENT_EDITORS = 10
    OPERATION_BATCH_SIZE = 20
    AWARENESS_CLEANUP_INTERVAL = 30000  // 30 seconds

DATA STRUCTURES:
    CollaborativeDocument:
        - id: string
        - content: string
        - version: number
        - participants: Map<userId, UserPresence>
        - operationLog: array<Operation>
        - conflictResolution: ConflictState
    
    Operation:
        - id: string
        - type: enum  // "insert", "delete", "format", "vocabulary_add"
        - position: number
        - content: string
        - userId: string
        - timestamp: number
        - version: number
    
    UserPresence:
        - userId: string
        - name: string
        - avatar: string
        - cursor: {position: number, selection: Range}
        - isActive: boolean
        - lastSeen: timestamp
        - color: string

BEGIN_ALGORITHM: CollaborativeFeatureManager

    INITIALIZATION:
        supabaseRealtime ← SupabaseRealtimeClient()
        operationalTransform ← OperationalTransformEngine()
        presenceManager ← PresenceManager()
        conflictResolver ← ConflictResolver()
        documentState ← Map<documentId, CollaborativeDocument>()

    FUNCTION: initializeCollaboration(documentId, userId)
        BEGIN
            // Set up real-time subscription
            channel ← supabaseRealtime.channel(`document:${documentId}`)
            
            // Join presence
            presenceState ← {
                userId: userId,
                name: getUserName(userId),
                avatar: getUserAvatar(userId),
                cursor: null,
                isActive: true,
                lastSeen: getCurrentTimestamp(),
                color: generateUserColor(userId)
            }
            
            channel.on("presence", { event: "sync" }, (payload) => {
                syncPresenceState(documentId, payload)
            })
            
            channel.on("presence", { event: "join" }, (payload) => {
                handleUserJoin(documentId, payload)
            })
            
            channel.on("presence", { event: "leave" }, (payload) => {
                handleUserLeave(documentId, payload)
            })
            
            // Operation synchronization
            channel.on("broadcast", { event: "operation" }, (payload) => {
                handleRemoteOperation(documentId, payload.operation)
            })
            
            channel.on("broadcast", { event: "vocabulary_update" }, (payload) => {
                handleVocabularyCollaboration(documentId, payload)
            })
            
            // Subscribe and track presence
            channel.subscribe((status) => {
                IF status === "SUBSCRIBED" THEN
                    channel.track(presenceState)
                    initializeDocumentState(documentId, userId)
                END IF
            })
            
            // Set up periodic presence updates
            setInterval(() => {
                updatePresence(documentId, userId)
            }, PRESENCE_UPDATE_INTERVAL)
            
            RETURN channel
        END
    END FUNCTION

    FUNCTION: handleLocalOperation(documentId, operation)
        BEGIN
            document ← documentState.get(documentId)
            
            // Apply operation locally (optimistic update)
            localResult ← applyOperationLocally(document, operation)
            
            // Update UI immediately
            updateCollaborativeUI(documentId, localResult)
            
            // Transform operation against concurrent operations
            transformedOperation ← operationalTransform.transform(
                operation, 
                document.operationLog.slice(operation.version)
            )
            
            // Broadcast to other participants
            broadcastOperation(documentId, transformedOperation)
            
            // Store in operation log
            document.operationLog.append(transformedOperation)
            document.version ← document.version + 1
            
            // Persist to Supabase
            persistOperationToSupabase(documentId, transformedOperation)
            
            RETURN localResult
        END
    END FUNCTION

    FUNCTION: handleRemoteOperation(documentId, remoteOperation)
        BEGIN
            document ← documentState.get(documentId)
            
            // Check for conflicts
            localOperations ← document.operationLog.filter(
                op => op.version > remoteOperation.version AND op.userId !== remoteOperation.userId
            )
            
            IF localOperations.length > 0 THEN
                // Resolve conflicts using Operational Transformation
                resolvedOperation ← resolveOperationConflicts(remoteOperation, localOperations)
            ELSE
                resolvedOperation ← remoteOperation
            END IF
            
            // Apply remote operation
            remoteResult ← applyOperationLocally(document, resolvedOperation)
            
            // Update UI with remote changes
            updateCollaborativeUI(documentId, remoteResult, {
                isRemote: true,
                userId: resolvedOperation.userId,
                userColor: getUserColor(resolvedOperation.userId)
            })
            
            // Update document state
            document.operationLog.append(resolvedOperation)
            document.version ← Math.max(document.version, resolvedOperation.version) + 1
            
            RETURN remoteResult
        END
    END FUNCTION

    FUNCTION: resolveOperationConflicts(remoteOperation, localOperations)
        BEGIN
            // Use Operational Transformation to resolve conflicts
            resolvedOperation ← remoteOperation
            
            FOR EACH localOp IN localOperations DO
                // Transform remote operation against local operation
                IF operationsConflict(resolvedOperation, localOp) THEN
                    transformResult ← operationalTransform.transformPair(
                        resolvedOperation, 
                        localOp
                    )
                    
                    resolvedOperation ← transformResult.remote
                    
                    // Also transform local operation if needed
                    IF transformResult.localNeedsUpdate THEN
                        updateLocalOperation(localOp, transformResult.local)
                    END IF
                END IF
            END FOR
            
            RETURN resolvedOperation
        END
    END FUNCTION

    FUNCTION: operationsConflict(op1, op2)
        BEGIN
            // Check if operations affect overlapping regions
            IF op1.type === "insert" AND op2.type === "insert" THEN
                RETURN op1.position === op2.position
            END IF
            
            IF op1.type === "delete" AND op2.type === "delete" THEN
                range1 ← [op1.position, op1.position + op1.content.length]
                range2 ← [op2.position, op2.position + op2.content.length]
                RETURN rangesOverlap(range1, range2)
            END IF
            
            IF (op1.type === "insert" AND op2.type === "delete") OR
               (op1.type === "delete" AND op2.type === "insert") THEN
                RETURN positionsConflict(op1, op2)
            END IF
            
            RETURN false
        END
    END FUNCTION

    FUNCTION: handleVocabularyCollaboration(documentId, payload)
        BEGIN
            vocabularyUpdate ← payload.vocabularyUpdate
            userId ← payload.userId
            
            SWITCH vocabularyUpdate.type
                CASE "word_added":
                    handleCollaborativeWordAddition(documentId, vocabularyUpdate, userId)
                    
                CASE "translation_improved":
                    handleCollaborativeTranslationUpdate(documentId, vocabularyUpdate, userId)
                    
                CASE "difficulty_voted":
                    handleCollaborativeDifficultyVoting(documentId, vocabularyUpdate, userId)
                    
                CASE "context_shared":
                    handleCollaborativeContextSharing(documentId, vocabularyUpdate, userId)
            END SWITCH
        END
    END FUNCTION

    FUNCTION: handleCollaborativeWordAddition(documentId, update, userId)
        BEGIN
            word ← update.word
            
            // Check if word already exists in collaborative vocabulary
            existingEntry ← getCollaborativeVocabularyEntry(documentId, word.text)
            
            IF existingEntry THEN
                // Merge with existing entry
                mergedEntry ← mergeVocabularyEntries(existingEntry, word, userId)
                updateCollaborativeVocabulary(documentId, mergedEntry)
            ELSE
                // Add new word with contributor information
                newEntry ← {
                    ...word,
                    contributors: [userId],
                    addedBy: userId,
                    addedAt: getCurrentTimestamp(),
                    votes: new Map()
                }
                
                addToCollaborativeVocabulary(documentId, newEntry)
            END IF
            
            // Show notification to other users
            showCollaborationNotification(documentId, {
                type: "vocabulary_added",
                message: `${getUserName(userId)} added "${word.text}" to vocabulary`,
                userId: userId,
                word: word.text
            })
        END
    END FUNCTION

    FUNCTION: updatePresence(documentId, userId)
        BEGIN
            document ← documentState.get(documentId)
            userPresence ← document.participants.get(userId)
            
            IF userPresence THEN
                // Update cursor position
                currentCursor ← getCurrentCursorPosition()
                userPresence.cursor ← currentCursor
                userPresence.lastSeen ← getCurrentTimestamp()
                userPresence.isActive ← isUserActivelyEditing()
                
                // Broadcast presence update
                channel ← getDocumentChannel(documentId)
                channel.track(userPresence)
                
                // Update presence UI for all users
                updatePresenceUI(documentId, document.participants)
            END IF
        END
    END FUNCTION

    FUNCTION: generateActivityFeed(documentId)
        BEGIN
            document ← documentState.get(documentId)
            activities ← []
            
            // Recent operations
            recentOps ← document.operationLog
                .filter(op => op.timestamp > Date.now() - 3600000)  // Last hour
                .sort((a, b) => b.timestamp - a.timestamp)
                .slice(0, 20)
            
            FOR EACH op IN recentOps DO
                activity ← formatOperationAsActivity(op)
                activities.append(activity)
            END FOR
            
            // Vocabulary contributions
            vocabularyActivities ← getRecentVocabularyActivities(documentId)
            activities ← activities.concat(vocabularyActivities)
            
            // Sort by timestamp
            activities.sort((a, b) => b.timestamp - a.timestamp)
            
            RETURN activities
        END
    END FUNCTION

    FUNCTION: handleUserJoin(documentId, payload)
        BEGIN
            newUser ← payload.newPresences[0]
            
            // Add to document participants
            document ← documentState.get(documentId)
            document.participants.set(newUser.userId, newUser)
            
            // Show join notification
            showCollaborationNotification(documentId, {
                type: "user_joined",
                message: `${newUser.name} joined the session`,
                userId: newUser.userId
            })
            
            // Update presence UI
            updatePresenceUI(documentId, document.participants)
            
            // Send current document state to new user
            sendDocumentStateToUser(documentId, newUser.userId)
        END
    END FUNCTION

    FUNCTION: handleUserLeave(documentId, payload)
        BEGIN
            leftUser ← payload.leftPresences[0]
            
            // Remove from document participants
            document ← documentState.get(documentId)
            document.participants.delete(leftUser.userId)
            
            // Show leave notification
            showCollaborationNotification(documentId, {
                type: "user_left",
                message: `${leftUser.name} left the session`,
                userId: leftUser.userId
            })
            
            // Update presence UI
            updatePresenceUI(documentId, document.participants)
            
            // Clean up user-specific UI elements
            cleanupUserPresenceUI(documentId, leftUser.userId)
        END
    END FUNCTION

    FUNCTION: optimisticUIUpdate(documentId, operation, isLocal = true)
        BEGIN
            // Immediately apply visual changes
            element ← getDocumentElement(documentId)
            
            SWITCH operation.type
                CASE "insert":
                    insertTextAtPosition(element, operation.position, operation.content, {
                        userId: operation.userId,
                        color: getUserColor(operation.userId),
                        isLocal: isLocal
                    })
                    
                CASE "delete":
                    deleteTextAtPosition(element, operation.position, operation.content.length, {
                        userId: operation.userId,
                        isLocal: isLocal
                    })
                    
                CASE "vocabulary_add":
                    highlightVocabularyWord(element, operation.word, {
                        userId: operation.userId,
                        color: getUserColor(operation.userId)
                    })
            END SWITCH
            
            // Show temporary visual feedback for remote changes
            IF NOT isLocal THEN
                showRemoteChangeIndicator(element, operation.position, operation.userId)
            END IF
        END
    END FUNCTION

    // Conflict resolution for complex scenarios
    CONFLICT_RESOLVER: conflictResolver
        BEGIN
            pendingConflicts ← Map<conflictId, ConflictState>()
            
            FUNCTION: detectConflict(operation1, operation2)
                // Advanced conflict detection beyond simple position overlap
                conflict ← {
                    id: generateConflictId(),
                    type: determineConflictType(operation1, operation2),
                    operations: [operation1, operation2],
                    severity: calculateConflictSeverity(operation1, operation2),
                    resolutionStrategies: getAvailableStrategies(operation1, operation2)
                }
                
                RETURN conflict
            END FUNCTION
            
            FUNCTION: resolveAutomatically(conflict)
                // Attempt automatic resolution based on conflict type
                SWITCH conflict.type
                    CASE "concurrent_insert":
                        RETURN resolveInsertConflict(conflict)
                        
                    CASE "edit_delete_conflict":
                        RETURN resolveEditDeleteConflict(conflict)
                        
                    CASE "vocabulary_duplicate":
                        RETURN mergeVocabularyConflict(conflict)
                        
                    DEFAULT:
                        RETURN null  // Requires manual resolution
                END SWITCH
            END FUNCTION
            
            FUNCTION: promptUserResolution(conflict)
                // Show conflict resolution UI to users
                conflictDialog ← createConflictResolutionDialog(conflict)
                conflictDialog.show()
                
                // Return promise that resolves when user makes choice
                RETURN new Promise((resolve) => {
                    conflictDialog.onResolution = (resolution) => {
                        resolve(resolution)
                    }
                })
            END FUNCTION
        END

    // Real-time synchronization with Supabase
    SUPABASE_SYNC: supabaseSync
        BEGIN
            FUNCTION: persistOperationToSupabase(documentId, operation)
                // Batch operations for efficiency
                operationBatch ← getOperationBatch(documentId)
                operationBatch.append(operation)
                
                IF operationBatch.length >= OPERATION_BATCH_SIZE THEN
                    flushOperationBatch(documentId, operationBatch)
                END IF
            END FUNCTION
            
            FUNCTION: flushOperationBatch(documentId, operations)
                supabase.from('collaborative_operations')
                    .insert(operations.map(op => ({
                        document_id: documentId,
                        operation_id: op.id,
                        type: op.type,
                        position: op.position,
                        content: op.content,
                        user_id: op.userId,
                        version: op.version,
                        timestamp: op.timestamp
                    })))
                    .then(response => {
                        handlePersistenceSuccess(documentId, operations)
                    })
                    .catch(error => {
                        handlePersistenceError(documentId, operations, error)
                    })
            END FUNCTION
        END

END_ALGORITHM

COMPLEXITY_ANALYSIS:
    Time Complexity:
        - Operation application: O(1) for local, O(n) for transformation
        - Conflict resolution: O(k²) where k = conflicting operations
        - Presence updates: O(p) where p = participants
        - Activity feed generation: O(a log a) where a = activities
        - UI updates: O(1) with optimistic updates
    
    Space Complexity:
        - Document state: O(d + o) where d = document size, o = operations
        - Presence tracking: O(p) where p = participants
        - Operation log: O(h) where h = history length
        - Conflict queue: O(c) where c = pending conflicts
    
    Performance Optimizations:
        - Operational Transformation for efficient conflict resolution
        - Optimistic UI updates for immediate feedback
        - Batched persistence to reduce database calls
        - Presence throttling to minimize network traffic
        - LRU cleanup of old operations and presence data
        - Web Workers for heavy transformation calculations
```

---

## INTEGRATION CONSIDERATIONS

### PWA-Specific Optimizations
1. **Service Worker Integration**: All algorithms designed to work offline-first
2. **IndexedDB Usage**: Local storage for vocabulary, images, and sync queue
3. **Background Sync**: Automatic synchronization when connectivity resumes
4. **Push Notifications**: Real-time collaboration notifications
5. **Responsive Design**: Algorithms adapt to mobile constraints

### Supabase Integration Points
1. **Real-time Subscriptions**: WebSocket connections for live collaboration
2. **Row Level Security**: User-based access control for vocabulary and sessions
3. **Storage Integration**: Cached image management with Supabase Storage
4. **Edge Functions**: Server-side processing for AI operations
5. **Database Triggers**: Automatic conflict resolution and data validation

### Performance Considerations
1. **Web Workers**: Heavy computations moved off main thread
2. **Virtual Scrolling**: Efficient rendering of large vocabulary lists
3. **Debouncing**: Reduced API calls and UI updates
4. **Progressive Enhancement**: Core functionality works without JavaScript
5. **Bundle Splitting**: Lazy loading of non-critical features

These algorithms provide the foundation for a robust, offline-first PWA with advanced collaborative features and seamless Supabase integration. Each algorithm includes comprehensive error handling, performance optimizations, and scalability considerations suitable for production deployment.