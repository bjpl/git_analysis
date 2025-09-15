# Real-World Search Algorithms: Part 2

## Image Recognition Search

### 📷 Visual Search Engine (KD-Tree for Feature Matching)
**Purpose**: Finds similar images based on visual features
**Real Usage**: Google Lens, Pinterest Visual Search, TinEye

```pseudocode
╔════════════════════════════════════════════════════════════════════╗
║ ALGORITHM: Image Similarity Search with KD-Trees and SIFT         ║
║ Database: 100M+ images | Query Time: <500ms | Accuracy: 92%       ║
╚════════════════════════════════════════════════════════════════════╝

▶ INPUT PARAMETERS:
  query_image: Image                 # Input image to search
  image_database: array[ImageRecord] # Pre-indexed image collection
  kd_tree: KDTree                   # Spatial index of features
  similarity_threshold: float        # Minimum similarity score
  max_results: int                   # Number of results to return
  
▶ OUTPUT:
  matches: array[ImageMatch]         # Similar images found
  bounding_boxes: array[Rectangle]   # Object locations in matches
  confidence_scores: array[float]    # Match confidence levels

▶ DATA STRUCTURES:
  Image: {
    pixels: array[array[RGB]]        # Raw pixel data
    width: int
    height: int
    metadata: ImageMetadata
  }
  
  ImageRecord: {
    id: string
    features: array[FeatureVector]   # SIFT/SURF/ORB descriptors
    global_descriptor: array[float]  # Color histogram, GIST, etc.
    thumbnail: Image
    source_url: string
  }
  
  FeatureVector: {
    keypoint: Point2D                # x, y location
    scale: float                     # Feature scale
    orientation: float               # Dominant orientation
    descriptor: array[float]         # 128D SIFT descriptor
  }
  
  KDNode: {
    point: FeatureVector
    left: KDNode
    right: KDNode
    split_dim: int                   # Dimension to split on
    image_id: string                 # Source image reference
  }

▶ ALGORITHM PART 1: Feature Extraction
FUNCTION extractImageFeatures(image):
    
    ══════ STEP 1: Build Gaussian Scale Space ══════
    # Create multi-scale representation
    num_octaves ← 4
    scales_per_octave ← 5
    initial_sigma ← 1.6
    
    scale_space ← []
    
    FOR octave FROM 0 TO num_octaves-1:
        octave_images ← []
        base_image ← downsample(image, 2^octave)
        
        FOR scale FROM 0 TO scales_per_octave-1:
            sigma ← initial_sigma × 2^(octave + scale/scales_per_octave)
            blurred ← gaussianBlur(base_image, sigma)
            octave_images.append(blurred)
        
        scale_space.append(octave_images)
    
    ══════ STEP 2: Detect Keypoints (SIFT) ══════
    keypoints ← []
    
    # Compute Difference of Gaussians (DoG)
    FOR octave FROM 0 TO num_octaves-1:
        FOR scale FROM 1 TO scales_per_octave-2:
            # DoG approximates Laplacian of Gaussian
            dog ← scale_space[octave][scale+1] - scale_space[octave][scale]
            
            # Find local extrema
            FOR y FROM 1 TO height(dog)-2:
                FOR x FROM 1 TO width(dog)-2:
                    pixel ← dog[y][x]
                    
                    # Check if extremum in 3x3x3 neighborhood
                    is_extremum ← TRUE
                    
                    # Check spatial neighbors
                    FOR dy FROM -1 TO 1:
                        FOR dx FROM -1 TO 1:
                            IF dy == 0 AND dx == 0:
                                CONTINUE
                            
                            neighbor ← dog[y+dy][x+dx]
                            IF (pixel > 0 AND neighbor >= pixel) OR
                               (pixel < 0 AND neighbor <= pixel):
                                is_extremum ← FALSE
                                BREAK
                    
                    # Check scale neighbors
                    IF is_extremum:
                        above ← scale_space[octave][scale+2][y][x]
                        below ← scale_space[octave][scale][y][x]
                        
                        IF (pixel > 0 AND (above >= pixel OR below >= pixel)) OR
                           (pixel < 0 AND (above <= pixel OR below <= pixel)):
                            is_extremum ← FALSE
                    
                    IF is_extremum AND ABS(pixel) > 0.03:  # Threshold
                        keypoint ← refineKeypoint(x, y, octave, scale, dog)
                        IF keypoint != NULL:
                            keypoints.append(keypoint)
    
    ══════ STEP 3: Compute Descriptors ══════
    features ← []
    
    FOR keypoint IN keypoints:
        # Compute gradient magnitude and orientation
        image_patch ← getImagePatch(
            scale_space[keypoint.octave][keypoint.scale],
            keypoint.x,
            keypoint.y,
            16  # 16x16 patch
        )
        
        # Rotate patch to canonical orientation
        rotated_patch ← rotatePatch(image_patch, -keypoint.orientation)
        
        # Build 128D descriptor (4x4 grid of 8-bin histograms)
        descriptor ← array[128]
        descriptor_index ← 0
        
        FOR grid_y FROM 0 TO 3:
            FOR grid_x FROM 0 TO 3:
                # Get 4x4 sub-patch
                sub_patch ← rotated_patch[grid_y*4:(grid_y+1)*4, grid_x*4:(grid_x+1)*4]
                
                # Compute gradient histogram
                histogram ← array[8]  # 8 orientation bins
                
                FOR y FROM 0 TO 3:
                    FOR x FROM 0 TO 3:
                        dx ← sub_patch[y][x+1] - sub_patch[y][x-1]
                        dy ← sub_patch[y+1][x] - sub_patch[y-1][x]
                        
                        magnitude ← sqrt(dx² + dy²)
                        orientation ← atan2(dy, dx)
                        
                        # Add to histogram with Gaussian weighting
                        bin ← FLOOR(orientation / (2π/8))
                        weight ← magnitude × gaussian(x-1.5, y-1.5, 1.5)
                        histogram[bin] += weight
                
                # Add to descriptor
                FOR bin FROM 0 TO 7:
                    descriptor[descriptor_index] ← histogram[bin]
                    descriptor_index += 1
        
        # Normalize descriptor
        norm ← sqrt(SUM(descriptor[i]² for i in 0..127))
        FOR i FROM 0 TO 127:
            descriptor[i] ← descriptor[i] / norm
            # Threshold to reduce illumination effects
            descriptor[i] ← MIN(descriptor[i], 0.2)
        
        # Renormalize
        norm ← sqrt(SUM(descriptor[i]² for i in 0..127))
        FOR i FROM 0 TO 127:
            descriptor[i] ← descriptor[i] / norm
        
        features.append(FeatureVector{
            keypoint: Point2D(keypoint.x, keypoint.y),
            scale: keypoint.scale,
            orientation: keypoint.orientation,
            descriptor: descriptor
        })
    
    RETURN features
END FUNCTION

▶ ALGORITHM PART 2: KD-Tree Construction (Offline)
FUNCTION buildKDTree(all_features, max_depth=40):
    
    ══════ Build Balanced KD-Tree ══════
    FUNCTION buildNode(features, depth):
        IF length(features) == 0:
            RETURN NULL
        
        IF length(features) == 1:
            RETURN KDNode{
                point: features[0],
                left: NULL,
                right: NULL,
                split_dim: -1,
                image_id: features[0].image_id
            }
        
        # Choose splitting dimension (cycle through dimensions)
        k ← 128  # Dimensionality of SIFT descriptors
        split_dim ← depth % k
        
        # For high dimensions, use dimension with highest variance
        IF depth < 10:  # Only for top levels
            variances ← []
            FOR dim FROM 0 TO k-1:
                values ← [f.descriptor[dim] FOR f IN features]
                variance ← calculateVariance(values)
                variances.append(variance)
            split_dim ← argmax(variances)
        
        # Sort by splitting dimension
        features ← SORT(features, key=lambda f: f.descriptor[split_dim])
        
        # Find median
        median_idx ← length(features) / 2
        median_feature ← features[median_idx]
        
        # Recursively build subtrees
        left_features ← features[0:median_idx]
        right_features ← features[median_idx+1:]
        
        node ← KDNode{
            point: median_feature,
            split_dim: split_dim,
            image_id: median_feature.image_id,
            left: buildNode(left_features, depth + 1),
            right: buildNode(right_features, depth + 1)
        }
        
        RETURN node
    END FUNCTION
    
    RETURN buildNode(all_features, 0)
END FUNCTION

▶ ALGORITHM PART 3: Image Search
FUNCTION searchSimilarImages(query_image, kd_tree, database, similarity_threshold, max_results):
    
    ══════ STEP 1: Extract Query Features ══════
    query_features ← extractImageFeatures(query_image)
    
    IF length(query_features) == 0:
        RETURN []  # No features found
    
    ══════ STEP 2: Find Nearest Neighbors for Each Feature ══════
    # For each query feature, find k nearest neighbors
    k_neighbors ← 2  # Ratio test requires 2 nearest
    feature_matches ← []
    
    FOR query_feature IN query_features:
        neighbors ← kdTreeKNN(kd_tree, query_feature, k_neighbors)
        
        IF length(neighbors) >= 2:
            # Lowe's ratio test - filter ambiguous matches
            best_distance ← euclideanDistance(query_feature.descriptor, neighbors[0].descriptor)
            second_distance ← euclideanDistance(query_feature.descriptor, neighbors[1].descriptor)
            
            IF best_distance < 0.7 × second_distance:  # Good match
                feature_matches.append({
                    query: query_feature,
                    match: neighbors[0],
                    distance: best_distance,
                    image_id: neighbors[0].image_id
                })
    
    ══════ STEP 3: Aggregate Matches by Image ══════
    image_votes ← HashMap()  # image_id -> array[matches]
    
    FOR match IN feature_matches:
        IF match.image_id NOT IN image_votes:
            image_votes[match.image_id] ← []
        image_votes[match.image_id].append(match)
    
    ══════ STEP 4: Geometric Verification (RANSAC) ══════
    verified_matches ← []
    
    FOR image_id, matches IN image_votes.items():
        IF length(matches) < 4:  # Need at least 4 for homography
            CONTINUE
        
        # Extract point correspondences
        src_points ← [m.query.keypoint FOR m IN matches]
        dst_points ← [m.match.keypoint FOR m IN matches]
        
        # RANSAC to find homography
        best_inliers ← []
        best_homography ← NULL
        max_iterations ← 1000
        
        FOR iteration FROM 0 TO max_iterations:
            # Random sample of 4 matches
            sample_indices ← randomSample(range(length(matches)), 4)
            sample_src ← [src_points[i] FOR i IN sample_indices]
            sample_dst ← [dst_points[i] FOR i IN sample_indices]
            
            # Compute homography from 4 points
            H ← computeHomography(sample_src, sample_dst)
            
            IF H == NULL:
                CONTINUE
            
            # Count inliers
            inliers ← []
            FOR i FROM 0 TO length(matches)-1:
                projected ← H × src_points[i]
                error ← euclideanDistance(projected, dst_points[i])
                
                IF error < 5.0:  # Pixel threshold
                    inliers.append(i)
            
            IF length(inliers) > length(best_inliers):
                best_inliers ← inliers
                best_homography ← H
            
            # Early termination if good enough
            IF length(best_inliers) > 0.8 × length(matches):
                BREAK
        
        # Keep only geometrically consistent matches
        IF length(best_inliers) >= 10:
            verified_matches.append({
                image_id: image_id,
                num_matches: length(best_inliers),
                homography: best_homography,
                inlier_matches: [matches[i] FOR i IN best_inliers]
            })
    
    ══════ STEP 5: Rank Results ══════
    results ← []
    
    FOR match IN verified_matches:
        # Compute similarity score
        score ← 0.0
        
        # Feature match score
        feature_score ← match.num_matches / length(query_features)
        feature_score ← MIN(feature_score, 1.0)
        
        # Geometric consistency score
        geometric_score ← calculateHomographyQuality(match.homography)
        
        # Global descriptor similarity (color histogram, etc.)
        db_image ← database.getImage(match.image_id)
        global_sim ← compareGlobalDescriptors(
            query_image.global_descriptor,
            db_image.global_descriptor
        )
        
        # Combined score
        score ← (feature_score × 0.5 + 
                geometric_score × 0.3 + 
                global_sim × 0.2)
        
        IF score >= similarity_threshold:
            results.append(ImageMatch{
                image_id: match.image_id,
                score: score,
                matched_features: match.num_matches,
                homography: match.homography
            })
    
    # Sort by score
    results ← SORT(results, key=score, descending=True)
    
    ══════ STEP 6: Generate Bounding Boxes ══════
    bounding_boxes ← []
    
    FOR result IN results[:max_results]:
        # Transform query image corners using homography
        h, w ← query_image.height, query_image.width
        corners ← [
            Point2D(0, 0),
            Point2D(w, 0),
            Point2D(w, h),
            Point2D(0, h)
        ]
        
        transformed_corners ← []
        FOR corner IN corners:
            transformed ← result.homography × corner
            transformed_corners.append(transformed)
        
        bbox ← boundingBox(transformed_corners)
        bounding_boxes.append(bbox)
    
    RETURN results[:max_results], bounding_boxes
END FUNCTION

▶ HELPER FUNCTION: KD-Tree K-Nearest Neighbors
FUNCTION kdTreeKNN(root, query_point, k):
    best_neighbors ← PriorityQueue(max_size=k)  # Max heap by distance
    
    FUNCTION searchNode(node, depth):
        IF node == NULL:
            RETURN
        
        # Calculate distance to current node
        distance ← euclideanDistance(query_point.descriptor, node.point.descriptor)
        
        # Add to best neighbors if within top k
        IF best_neighbors.size() < k:
            best_neighbors.push((distance, node.point))
        ELSE IF distance < best_neighbors.top().distance:
            best_neighbors.pop()
            best_neighbors.push((distance, node.point))
        
        # Determine which subtree to search first
        split_dim ← node.split_dim
        IF split_dim == -1:  # Leaf node
            RETURN
        
        diff ← query_point.descriptor[split_dim] - node.point.descriptor[split_dim]
        
        IF diff < 0:
            first_subtree ← node.left
            second_subtree ← node.right
        ELSE:
            first_subtree ← node.right
            second_subtree ← node.left
        
        # Search closer subtree first
        searchNode(first_subtree, depth + 1)
        
        # Check if we need to search other subtree
        IF best_neighbors.size() < k OR ABS(diff) < best_neighbors.top().distance:
            searchNode(second_subtree, depth + 1)
    END FUNCTION
    
    searchNode(root, 0)
    
    # Extract sorted results
    results ← []
    WHILE NOT best_neighbors.isEmpty():
        results.prepend(best_neighbors.pop().point)
    
    RETURN results
END FUNCTION

▶ OPTIMIZATIONS:
  • Use approximate nearest neighbors (FLANN, Annoy)
  • Hierarchical vocabulary tree for large-scale search
  • GPU acceleration for feature extraction
  • Inverted file index for billion-scale datasets
  • Product quantization for compact descriptors
  • Cascade filtering with cheap features first
```

---

## Game AI Pathfinding

### 🎮 Game Pathfinding (Jump Point Search)
**Purpose**: Ultra-fast pathfinding for video game characters
**Real Usage**: StarCraft II, Civilization VI, Path of Exile

```pseudocode
╔════════════════════════════════════════════════════════════════════╗
║ ALGORITHM: Jump Point Search (JPS) for Grid Pathfinding           ║
║ Performance: 10-30x faster than A* | Memory: O(n) | Grid: 1000x1000║
╚════════════════════════════════════════════════════════════════════╝

▶ INPUT PARAMETERS:
  grid: Grid2D[Cell]                 # Game map grid
  start: GridPosition                # Starting position
  goal: GridPosition                 # Target position
  unit_size: int                     # Unit collision radius
  movement_type: MovementType        # Walk, fly, swim, etc.
  
▶ OUTPUT:
  path: array[GridPosition]          # Optimal path
  waypoints: array[GridPosition]     # Smoothed path points
  cost: float                        # Total path cost

▶ DATA STRUCTURES:
  Cell: {
    walkable: boolean
    cost: float                     # Movement cost (terrain type)
    height: float                   # Elevation
    flags: bitfield                 # water, lava, fog, etc.
  }
  
  JPSNode: {
    position: GridPosition
    g_cost: float
    h_cost: float
    f_cost: float
    parent: JPSNode
    forced_neighbors: array[Direction]
  }
  
  Direction: enum {
    NORTH, NORTHEAST, EAST, SOUTHEAST,
    SOUTH, SOUTHWEST, WEST, NORTHWEST
  }

▶ ALGORITHM:
FUNCTION jumpPointSearch(grid, start, goal, unit_size, movement_type):
    
    ══════ STEP 1: Preprocess Grid for Unit Size ══════
    IF unit_size > 1:
        # Create clearance map for larger units
        clearance_grid ← computeClearanceMap(grid, unit_size)
        USE clearance_grid INSTEAD OF grid
    
    ══════ STEP 2: Initialize JPS ══════
    open_list ← PriorityQueue()  # Min heap by f_cost
    closed_set ← Set()
    
    start_node ← JPSNode{
        position: start,
        g_cost: 0,
        h_cost: octileDistance(start, goal),
        f_cost: h_cost,
        parent: NULL,
        forced_neighbors: []
    }
    
    open_list.push(start_node)
    
    ══════ STEP 3: Main JPS Loop ══════
    WHILE NOT open_list.isEmpty():
        current ← open_list.pop()
        
        IF current.position == goal:
            RETURN reconstructPath(current)
        
        closed_set.add(current.position)
        
        # Identify successors (jump points)
        successors ← identifySuccessors(current, grid, goal)
        
        FOR successor IN successors:
            IF successor.position IN closed_set:
                CONTINUE
            
            # Calculate jump cost
            jump_cost ← calculateJumpCost(
                current.position,
                successor.position,
                grid
            )
            
            tentative_g ← current.g_cost + jump_cost
            
            # Check if we found a better path
            existing ← findInOpenList(open_list, successor.position)
            IF existing != NULL:
                IF tentative_g >= existing.g_cost:
                    CONTINUE
                ELSE:
                    open_list.remove(existing)
            
            # Add successor to open list
            successor.g_cost ← tentative_g
            successor.h_cost ← octileDistance(successor.position, goal)
            successor.f_cost ← successor.g_cost + successor.h_cost
            successor.parent ← current
            
            open_list.push(successor)
    
    RETURN NULL  # No path found

    ══════ FUNCTION: Identify Successors (Core JPS Logic) ══════
    FUNCTION identifySuccessors(node, grid, goal):
        successors ← []
        neighbors ← []
        
        IF node.parent != NULL:
            # Get normalized direction from parent
            dx ← SIGN(node.position.x - node.parent.position.x)
            dy ← SIGN(node.position.y - node.parent.position.y)
            
            # Diagonal move
            IF dx != 0 AND dy != 0:
                # Check diagonal continuation
                IF isWalkable(grid, node.position.x + dx, node.position.y + dy):
                    neighbors.append(Direction(dx, dy))
                
                # Check horizontal component
                IF isWalkable(grid, node.position.x + dx, node.position.y):
                    neighbors.append(Direction(dx, 0))
                
                # Check vertical component
                IF isWalkable(grid, node.position.x, node.position.y + dy):
                    neighbors.append(Direction(0, dy))
                
                # Check for forced neighbors (diagonal case)
                IF NOT isWalkable(grid, node.position.x - dx, node.position.y) AND
                   isWalkable(grid, node.position.x - dx, node.position.y + dy):
                    neighbors.append(Direction(-dx, dy))
                
                IF NOT isWalkable(grid, node.position.x, node.position.y - dy) AND
                   isWalkable(grid, node.position.x + dx, node.position.y - dy):
                    neighbors.append(Direction(dx, -dy))
            
            # Straight move (horizontal or vertical)
            ELSE:
                IF dx == 0:  # Moving vertically
                    IF isWalkable(grid, node.position.x, node.position.y + dy):
                        neighbors.append(Direction(0, dy))
                    
                    # Check for forced neighbors
                    IF NOT isWalkable(grid, node.position.x + 1, node.position.y) AND
                       isWalkable(grid, node.position.x + 1, node.position.y + dy):
                        neighbors.append(Direction(1, dy))
                    
                    IF NOT isWalkable(grid, node.position.x - 1, node.position.y) AND
                       isWalkable(grid, node.position.x - 1, node.position.y + dy):
                        neighbors.append(Direction(-1, dy))
                
                ELSE:  # Moving horizontally
                    IF isWalkable(grid, node.position.x + dx, node.position.y):
                        neighbors.append(Direction(dx, 0))
                    
                    # Check for forced neighbors
                    IF NOT isWalkable(grid, node.position.x, node.position.y + 1) AND
                       isWalkable(grid, node.position.x + dx, node.position.y + 1):
                        neighbors.append(Direction(dx, 1))
                    
                    IF NOT isWalkable(grid, node.position.x, node.position.y - 1) AND
                       isWalkable(grid, node.position.x + dx, node.position.y - 1):
                        neighbors.append(Direction(dx, -1))
        
        ELSE:
            # No parent - consider all neighbors
            FOR direction IN ALL_DIRECTIONS:
                IF isWalkable(grid, node.position.x + direction.dx, 
                            node.position.y + direction.dy):
                    neighbors.append(direction)
        
        # Try to jump in each neighbor direction
        FOR direction IN neighbors:
            jump_point ← jump(node.position, direction, grid, goal)
            
            IF jump_point != NULL:
                successors.append(JPSNode{
                    position: jump_point,
                    parent: node
                })
        
        RETURN successors
    END FUNCTION
    
    ══════ FUNCTION: Jump (Find Jump Points) ══════
    FUNCTION jump(position, direction, grid, goal):
        next_x ← position.x + direction.dx
        next_y ← position.y + direction.dy
        
        # Check if position is walkable
        IF NOT isWalkable(grid, next_x, next_y):
            RETURN NULL
        
        next_pos ← GridPosition(next_x, next_y)
        
        # Check if we reached the goal
        IF next_pos == goal:
            RETURN next_pos
        
        # Check for forced neighbors
        IF direction.dx != 0 AND direction.dy != 0:  # Diagonal
            # Check horizontal forced neighbor
            IF (NOT isWalkable(grid, next_x - direction.dx, next_y) AND
                isWalkable(grid, next_x - direction.dx, next_y + direction.dy)) OR
               (NOT isWalkable(grid, next_x, next_y - direction.dy) AND
                isWalkable(grid, next_x + direction.dx, next_y - direction.dy)):
                RETURN next_pos
            
            # Recursively jump horizontally and vertically
            IF jump(next_pos, Direction(direction.dx, 0), grid, goal) != NULL OR
               jump(next_pos, Direction(0, direction.dy), grid, goal) != NULL:
                RETURN next_pos
        
        ELSE:  # Straight
            IF direction.dx != 0:  # Horizontal
                IF (NOT isWalkable(grid, next_x, next_y + 1) AND
                    isWalkable(grid, next_x + direction.dx, next_y + 1)) OR
                   (NOT isWalkable(grid, next_x, next_y - 1) AND
                    isWalkable(grid, next_x + direction.dx, next_y - 1)):
                    RETURN next_pos
            
            ELSE:  # Vertical
                IF (NOT isWalkable(grid, next_x + 1, next_y) AND
                    isWalkable(grid, next_x + 1, next_y + direction.dy)) OR
                   (NOT isWalkable(grid, next_x - 1, next_y) AND
                    isWalkable(grid, next_x - 1, next_y + direction.dy)):
                    RETURN next_pos
        
        # Continue jumping
        RETURN jump(next_pos, direction, grid, goal)
    END FUNCTION
END FUNCTION

▶ PATH SMOOTHING:
FUNCTION smoothPath(path, grid):
    IF length(path) <= 2:
        RETURN path
    
    waypoints ← [path[0]]
    current_index ← 0
    
    WHILE current_index < length(path) - 1:
        farthest_visible ← current_index + 1
        
        # Find farthest visible point
        FOR i FROM current_index + 2 TO length(path) - 1:
            IF hasLineOfSight(path[current_index], path[i], grid):
                farthest_visible ← i
            ELSE:
                BREAK
        
        waypoints.append(path[farthest_visible])
        current_index ← farthest_visible
    
    RETURN waypoints
END FUNCTION

FUNCTION hasLineOfSight(start, end, grid):
    # Bresenham's line algorithm
    x0, y0 ← start.x, start.y
    x1, y1 ← end.x, end.y
    
    dx ← ABS(x1 - x0)
    dy ← ABS(y1 - y0)
    sx ← 1 IF x0 < x1 ELSE -1
    sy ← 1 IF y0 < y1 ELSE -1
    err ← dx - dy
    
    WHILE TRUE:
        IF NOT isWalkable(grid, x0, y0):
            RETURN FALSE
        
        IF x0 == x1 AND y0 == y1:
            RETURN TRUE
        
        e2 ← 2 × err
        
        IF e2 > -dy:
            err ← err - dy
            x0 ← x0 + sx
        
        IF e2 < dx:
            err ← err + dx
            y0 ← y0 + sy
END FUNCTION

▶ OPTIMIZATIONS:
  • Preprocessing: Build jump point database offline
  • Hierarchical pathfinding for large maps
  • Goal bounding: Prune nodes outside goal direction
  • Parallel search for multiple units
  • Path caching for common routes
  • Incremental replanning for dynamic obstacles
```

---

## File System Search

### 📁 File Content Search (Boyer-Moore String Matching)
**Purpose**: Fast text search in files and documents
**Real Usage**: grep, Windows Search, IDE find-in-files

```pseudocode
╔════════════════════════════════════════════════════════════════════╗
║ ALGORITHM: Boyer-Moore with Wildcards and Regex Support           ║
║ Performance: O(n/m) average | Files: Millions | Speed: GB/s        ║
╚════════════════════════════════════════════════════════════════════╝

▶ INPUT PARAMETERS:
  pattern: string                    # Search pattern (may include wildcards)
  directory: DirectoryPath           # Root directory to search
  options: SearchOptions             # Case sensitivity, regex, etc.
  file_filters: array[string]        # File extensions to search
  
▶ OUTPUT:
  matches: array[FileMatch]          # Files containing matches
  line_matches: array[LineMatch]     # Specific line matches
  statistics: SearchStats            # Files searched, time taken

▶ DATA STRUCTURES:
  FileMatch: {
    file_path: string
    matches: array[LineMatch]
    file_size: long
    last_modified: datetime
  }
  
  LineMatch: {
    line_number: int
    column_start: int
    column_end: int
    line_text: string
    context_before: array[string]    # Previous lines for context
    context_after: array[string]     # Following lines for context
  }

▶ ALGORITHM PART 1: Boyer-Moore Preprocessing
FUNCTION preprocessPattern(pattern, case_sensitive):
    m ← length(pattern)
    
    IF NOT case_sensitive:
        pattern ← toLowerCase(pattern)
    
    ══════ Build Bad Character Table ══════
    bad_char ← array[256]  # ASCII table
    
    # Initialize all characters to pattern length
    FOR i FROM 0 TO 255:
        bad_char[i] ← m
    
    # Set shift values for pattern characters
    FOR i FROM 0 TO m-2:
        char ← pattern[i]
        bad_char[char] ← m - i - 1
        
        IF NOT case_sensitive:
            # Handle both cases
            upper ← toUpperCase(char)
            lower ← toLowerCase(char)
            bad_char[upper] ← m - i - 1
            bad_char[lower] ← m - i - 1
    
    ══════ Build Good Suffix Table ══════
    good_suffix ← array[m]
    
    # Compute suffix lengths
    suffix ← computeSuffixArray(pattern)
    
    # Case 1: Pattern contains another occurrence of suffix
    FOR i FROM 0 TO m-1:
        good_suffix[i] ← m
    
    j ← 0
    FOR i FROM m-1 TO 0 STEP -1:
        IF suffix[i] == i + 1:  # Prefix of pattern
            WHILE j < m - i - 1:
                IF good_suffix[j] == m:
                    good_suffix[j] ← m - i - 1
                j += 1
    
    # Case 2: Part of suffix occurs at beginning
    FOR i FROM 0 TO m-2:
        good_suffix[m - suffix[i] - 1] ← m - i - 1
    
    RETURN bad_char, good_suffix
END FUNCTION

▶ ALGORITHM PART 2: File System Traversal
FUNCTION searchFiles(pattern, directory, options, file_filters):
    
    # Preprocess pattern
    IF options.use_regex:
        regex ← compileRegex(pattern, options)
    ELSE:
        bad_char, good_suffix ← preprocessPattern(pattern, options.case_sensitive)
    
    matches ← []
    stats ← SearchStats{files_searched: 0, bytes_processed: 0, start_time: NOW()}
    
    ══════ Parallel File Search ══════
    file_queue ← Queue()
    result_queue ← Queue()
    
    # Start worker threads
    num_workers ← getNumCPUs()
    workers ← []
    
    FOR i FROM 0 TO num_workers-1:
        worker ← Thread(searchWorker, file_queue, result_queue, pattern, options)
        worker.start()
        workers.append(worker)
    
    # Traverse directory tree
    traverseDirectory(directory, file_queue, file_filters, options)
    
    # Signal workers to stop
    FOR i FROM 0 TO num_workers-1:
        file_queue.put(NULL)
    
    # Collect results
    active_workers ← num_workers
    WHILE active_workers > 0:
        result ← result_queue.get()
        
        IF result == NULL:
            active_workers -= 1
        ELSE:
            matches.append(result)
            stats.files_searched += 1
            stats.bytes_processed += result.file_size
    
    stats.end_time ← NOW()
    stats.duration ← stats.end_time - stats.start_time
    
    RETURN matches, stats
END FUNCTION

▶ ALGORITHM PART 3: Boyer-Moore Search in File
FUNCTION searchInFile(file_path, pattern, bad_char, good_suffix, options):
    file_matches ← []
    
    # Memory-map file for efficiency
    file_content ← memoryMapFile(file_path)
    n ← length(file_content)
    m ← length(pattern)
    
    IF n < m:
        RETURN []
    
    # Convert to lowercase if case-insensitive
    IF NOT options.case_sensitive:
        search_content ← toLowerCase(file_content)
    ELSE:
        search_content ← file_content
    
    # Boyer-Moore search
    i ← m - 1  # Position in text
    
    WHILE i < n:
        j ← m - 1  # Position in pattern
        
        # Match from right to left
        WHILE j >= 0 AND search_content[i] == pattern[j]:
            i -= 1
            j -= 1
        
        IF j < 0:
            # Match found
            match_start ← i + 1
            match_end ← match_start + m
            
            # Extract line context
            line_start ← findLineStart(file_content, match_start)
            line_end ← findLineEnd(file_content, match_end)
            line_number ← countLines(file_content, 0, line_start) + 1
            
            # Get context lines
            context_before ← []
            context_after ← []
            
            IF options.context_lines > 0:
                context_before ← getPreviousLines(
                    file_content,
                    line_start,
                    options.context_lines
                )
                context_after ← getNextLines(
                    file_content,
                    line_end,
                    options.context_lines
                )
            
            file_matches.append(LineMatch{
                line_number: line_number,
                column_start: match_start - line_start,
                column_end: match_end - line_start,
                line_text: file_content[line_start:line_end],
                context_before: context_before,
                context_after: context_after
            })
            
            # Move to next potential match
            i += m + 1
        
        ELSE:
            # Mismatch - use Boyer-Moore shift rules
            bad_char_shift ← bad_char[search_content[i]]
            good_suffix_shift ← good_suffix[j]
            
            shift ← MAX(bad_char_shift, good_suffix_shift)
            i += shift
    
    IF length(file_matches) > 0:
        RETURN FileMatch{
            file_path: file_path,
            matches: file_matches,
            file_size: n,
            last_modified: getFileModTime(file_path)
        }
    
    RETURN NULL
END FUNCTION

▶ ALGORITHM PART 4: Regex and Wildcard Support
FUNCTION searchWithRegex(file_path, regex, options):
    file_matches ← []
    
    # Read file line by line for regex
    file ← openFile(file_path)
    line_number ← 0
    
    WHILE line ← file.readLine():
        line_number += 1
        
        IF NOT options.case_sensitive:
            search_line ← toLowerCase(line)
        ELSE:
            search_line ← line
        
        # Find all regex matches in line
        matches ← regex.findAll(search_line)
        
        FOR match IN matches:
            # Get context if requested
            context_before ← []
            context_after ← []
            
            IF options.context_lines > 0:
                # Rewind file to get previous lines
                saved_position ← file.tell()
                context_before ← getPreviousLinesFromFile(
                    file,
                    line_number,
                    options.context_lines
                )
                
                # Get following lines
                file.seek(saved_position)
                context_after ← getNextLinesFromFile(
                    file,
                    options.context_lines
                )
                file.seek(saved_position)
            
            file_matches.append(LineMatch{
                line_number: line_number,
                column_start: match.start,
                column_end: match.end,
                line_text: line,
                context_before: context_before,
                context_after: context_after
            })
    
    file.close()
    
    IF length(file_matches) > 0:
        RETURN FileMatch{
            file_path: file_path,
            matches: file_matches,
            file_size: getFileSize(file_path),
            last_modified: getFileModTime(file_path)
        }
    
    RETURN NULL
END FUNCTION

▶ HELPER FUNCTIONS:
FUNCTION traverseDirectory(directory, file_queue, filters, options):
    # Iterative traversal with stack to avoid recursion limits
    dir_stack ← Stack()
    dir_stack.push(directory)
    
    WHILE NOT dir_stack.isEmpty():
        current_dir ← dir_stack.pop()
        
        TRY:
            entries ← listDirectory(current_dir)
            
            FOR entry IN entries:
                IF entry.is_directory:
                    IF NOT options.skip_hidden OR NOT entry.name.startsWith("."):
                        # Check if directory should be excluded
                        IF entry.name NOT IN options.exclude_dirs:
                            dir_stack.push(entry.path)
                
                ELSE:  # File
                    # Check file filters
                    IF matchesFilter(entry.name, filters):
                        IF NOT options.skip_binary OR NOT isBinary(entry.path):
                            file_queue.put(entry.path)
        
        CATCH PermissionError:
            # Skip directories we can't access
            CONTINUE
END FUNCTION

FUNCTION searchWorker(file_queue, result_queue, pattern, options):
    # Preprocess pattern for this thread
    IF options.use_regex:
        regex ← compileRegex(pattern, options)
    ELSE:
        bad_char, good_suffix ← preprocessPattern(pattern, options.case_sensitive)
    
    WHILE TRUE:
        file_path ← file_queue.get()
        
        IF file_path == NULL:
            result_queue.put(NULL)
            BREAK
        
        TRY:
            IF options.use_regex:
                result ← searchWithRegex(file_path, regex, options)
            ELSE:
                result ← searchInFile(file_path, pattern, bad_char, good_suffix, options)
            
            IF result != NULL:
                result_queue.put(result)
        
        CATCH Exception:
            # Skip files that can't be read
            CONTINUE
END FUNCTION

▶ OPTIMIZATIONS:
  • SIMD instructions for parallel character comparison
  • Memory-mapped I/O for large files
  • Skip binary files using magic bytes
  • Index frequently searched directories
  • Bloom filters for quick negative matches
  • Parallel directory traversal
  • Incremental indexing with file watching
```

---

## Similarity Search

### 🔎 Locality-Sensitive Hashing for Similarity Search
**Purpose**: Finds similar items in high-dimensional spaces
**Real Usage**: Spotify song recommendations, YouTube video suggestions, Shazam

```pseudocode
╔════════════════════════════════════════════════════════════════════╗
║ ALGORITHM: LSH for Audio/Document Similarity Search               ║
║ Dimensions: 1000+ | Dataset: 100M items | Accuracy: 90%           ║
╚════════════════════════════════════════════════════════════════════╝

▶ INPUT PARAMETERS:
  query_item: FeatureVector          # Query audio/document features
  database: array[Item]              # Collection of items
  lsh_index: LSHIndex               # Pre-built hash tables
  similarity_threshold: float        # Minimum similarity (0-1)
  num_results: int                   # Number of results to return
  
▶ OUTPUT:
  similar_items: array[SimilarItem]  # Ranked similar items
  explanations: array[string]        # Why items are similar

▶ DATA STRUCTURES:
  LSHIndex: {
    hash_tables: array[HashTable]    # Multiple hash tables
    hash_functions: array[array[HashFunction]]  # Functions per table
    num_tables: int                  # L parameter
    signature_length: int            # K parameter
  }
  
  HashTable: {
    buckets: HashMap[int, array[ItemID]]  # Hash -> item IDs
    function_family: string          # "minhash", "simhash", "p-stable"
  }
  
  AudioFeatures: {
    mfcc: array[float]              # Mel-frequency cepstral coefficients
    chroma: array[float]            # Pitch class profiles
    tempo: float
    spectral_centroid: array[float]
    zero_crossing_rate: float
  }

▶ ALGORITHM PART 1: Build LSH Index (Offline)
FUNCTION buildLSHIndex(database, num_tables=20, signature_length=10):
    
    ══════ STEP 1: Choose Hash Family Based on Similarity ══════
    sample_items ← randomSample(database, 100)
    feature_type ← detectFeatureType(sample_items)
    
    IF feature_type == "binary":
        hash_family ← "simhash"
    ELSE IF feature_type == "set":
        hash_family ← "minhash"
    ELSE:  # Continuous features
        hash_family ← "p-stable"
    
    ══════ STEP 2: Generate Hash Functions ══════
    lsh_index ← LSHIndex{
        hash_tables: [],
        hash_functions: [],
        num_tables: num_tables,
        signature_length: signature_length
    }
    
    FOR table_id FROM 0 TO num_tables-1:
        table_functions ← []
        
        FOR i FROM 0 TO signature_length-1:
            IF hash_family == "p-stable":
                # For Euclidean distance (L2)
                a ← randomGaussianVector(dimension)
                b ← randomUniform(0, width)
                w ← 4  # Bucket width
                
                hash_func ← FUNCTION(x):
                    RETURN FLOOR((dot(a, x) + b) / w)
                
            ELSE IF hash_family == "minhash":
                # For Jaccard similarity
                a ← randomInt(1, large_prime)
                b ← randomInt(0, large_prime)
                
                hash_func ← FUNCTION(x):
                    min_hash ← INFINITY
                    FOR element IN x:
                        hash_val ← (a × hash(element) + b) % large_prime
                        min_hash ← MIN(min_hash, hash_val)
                    RETURN min_hash
            
            ELSE IF hash_family == "simhash":
                # For cosine similarity
                random_hyperplane ← randomUnitVector(dimension)
                
                hash_func ← FUNCTION(x):
                    RETURN 1 IF dot(random_hyperplane, x) >= 0 ELSE 0
            
            table_functions.append(hash_func)
        
        lsh_index.hash_functions.append(table_functions)
        lsh_index.hash_tables.append(HashTable{buckets: HashMap()})
    
    ══════ STEP 3: Hash All Items ══════
    FOR item IN database:
        FOR table_id FROM 0 TO num_tables-1:
            # Compute signature for this table
            signature ← []
            
            FOR hash_func IN lsh_index.hash_functions[table_id]:
                hash_value ← hash_func(item.features)
                signature.append(hash_value)
            
            # Combine signature into single hash
            bucket_key ← hashSignature(signature)
            
            # Add to hash table
            IF bucket_key NOT IN lsh_index.hash_tables[table_id].buckets:
                lsh_index.hash_tables[table_id].buckets[bucket_key] ← []
            
            lsh_index.hash_tables[table_id].buckets[bucket_key].append(item.id)
    
    RETURN lsh_index
END FUNCTION

▶ ALGORITHM PART 2: Query Processing
FUNCTION findSimilarItems(query_item, lsh_index, database, threshold, num_results):
    
    ══════ STEP 1: Generate Query Signatures ══════
    candidate_set ← Set()
    
    FOR table_id FROM 0 TO lsh_index.num_tables-1:
        # Compute query signature for this table
        signature ← []
        
        FOR hash_func IN lsh_index.hash_functions[table_id]:
            hash_value ← hash_func(query_item.features)
            signature.append(hash_value)
        
        bucket_key ← hashSignature(signature)
        
        # Get candidates from this bucket
        IF bucket_key IN lsh_index.hash_tables[table_id].buckets:
            candidates ← lsh_index.hash_tables[table_id].buckets[bucket_key]
            candidate_set.update(candidates)
    
    ══════ STEP 2: Exact Distance Computation ══════
    similar_items ← []
    
    FOR candidate_id IN candidate_set:
        candidate ← database.getItem(candidate_id)
        
        # Compute exact similarity
        similarity ← computeSimilarity(query_item, candidate)
        
        IF similarity >= threshold:
            similar_items.append(SimilarItem{
                item: candidate,
                similarity: similarity,
                common_buckets: countCommonBuckets(query_item, candidate, lsh_index)
            })
    
    # Sort by similarity
    similar_items ← SORT(similar_items, key=similarity, descending=True)
    
    ══════ STEP 3: Multi-Probe LSH (Optional Enhancement) ══════
    IF length(similar_items) < num_results:
        # Probe nearby buckets
        additional_candidates ← multiProbe(
            query_item,
            lsh_index,
            num_probes=10
        )
        
        FOR candidate_id IN additional_candidates:
            IF candidate_id NOT IN candidate_set:
                candidate ← database.getItem(candidate_id)
                similarity ← computeSimilarity(query_item, candidate)
                
                IF similarity >= threshold:
                    similar_items.append(SimilarItem{
                        item: candidate,
                        similarity: similarity
                    })
    
    ══════ STEP 4: Generate Explanations ══════
    explanations ← []
    
    FOR item IN similar_items[:num_results]:
        explanation ← explainSimilarity(query_item, item.item)
        explanations.append(explanation)
    
    RETURN similar_items[:num_results], explanations
END FUNCTION

▶ SPECIALIZED: Audio Fingerprinting (Shazam-style)
FUNCTION audioFingerprint(audio_signal, sample_rate=44100):
    
    ══════ STEP 1: Spectrogram Generation ══════
    # Short-Time Fourier Transform
    window_size ← 4096
    hop_length ← window_size / 2
    spectrogram ← STFT(audio_signal, window_size, hop_length)
    
    ══════ STEP 2: Find Constellation Points ══════
    # Find peaks in spectrogram
    peaks ← []
    
    FOR time_frame FROM 0 TO length(spectrogram[0])-1:
        FOR freq_bin FROM 0 TO length(spectrogram)-1:
            magnitude ← ABS(spectrogram[freq_bin][time_frame])
            
            # Check if local maximum
            is_peak ← TRUE
            FOR dt FROM -2 TO 2:
                FOR df FROM -2 TO 2:
                    IF dt == 0 AND df == 0:
                        CONTINUE
                    
                    neighbor_time ← time_frame + dt
                    neighbor_freq ← freq_bin + df
                    
                    IF inBounds(neighbor_time, neighbor_freq, spectrogram):
                        IF ABS(spectrogram[neighbor_freq][neighbor_time]) >= magnitude:
                            is_peak ← FALSE
                            BREAK
            
            IF is_peak AND magnitude > threshold:
                peaks.append({
                    time: time_frame × hop_length / sample_rate,
                    frequency: freq_bin × sample_rate / window_size,
                    magnitude: magnitude
                })
    
    # Keep only strongest peaks
    peaks ← SORT(peaks, key=magnitude, descending=True)[:200]
    
    ══════ STEP 3: Generate Hashes from Peak Pairs ══════
    hashes ← []
    
    FOR i FROM 0 TO length(peaks)-1:
        anchor ← peaks[i]
        
        # Create target zone
        target_peaks ← []
        FOR j FROM i+1 TO MIN(i+20, length(peaks)-1):
            IF peaks[j].time - anchor.time > 0.2 AND
               peaks[j].time - anchor.time < 2.0:
                target_peaks.append(peaks[j])
        
        # Generate hashes from anchor-target pairs
        FOR target IN target_peaks[:3]:  # Limit fan-out
            hash_value ← packHash(
                anchor.frequency,
                target.frequency,
                target.time - anchor.time
            )
            
            hashes.append({
                hash: hash_value,
                time: anchor.time
            })
    
    RETURN hashes
END FUNCTION

▶ HELPER FUNCTIONS:
FUNCTION computeSimilarity(item1, item2):
    IF item1.type == "audio":
        # Use acoustic similarity
        RETURN acousticSimilarity(item1.features, item2.features)
    
    ELSE IF item1.type == "document":
        # Use cosine similarity for text
        RETURN cosineSimilarity(item1.features, item2.features)
    
    ELSE IF item1.type == "image":
        # Use perceptual hash distance
        RETURN 1 - hammingDistance(item1.phash, item2.phash) / 64
    
    ELSE:
        # Default to Euclidean distance
        distance ← euclideanDistance(item1.features, item2.features)
        RETURN 1 / (1 + distance)  # Convert to similarity
END FUNCTION

FUNCTION explainSimilarity(query, result):
    explanations ← []
    
    IF query.type == "audio":
        IF ABS(query.tempo - result.tempo) < 5:
            explanations.append(f"Similar tempo (~{result.tempo} BPM)")
        
        IF cosineSimilarity(query.chroma, result.chroma) > 0.8:
            explanations.append("Similar harmonic content")
        
        IF correlate(query.mfcc, result.mfcc) > 0.7:
            explanations.append("Similar timbre/instrumentation")
    
    ELSE IF query.type == "document":
        common_terms ← intersection(query.top_terms, result.top_terms)
        IF length(common_terms) > 0:
            explanations.append(f"Common topics: {JOIN(common_terms[:3])}")
    
    RETURN JOIN(explanations, "; ")
END FUNCTION

▶ OPTIMIZATIONS:
  • Use bit-packed signatures for memory efficiency
  • GPU acceleration for hash computation
  • Distributed hash tables for scale
  • Learned LSH functions using neural networks
  • Progressive refinement with multiple rounds
  • Cache popular queries
```

---

## Network Routing

### 🌐 Internet Routing (BGP Path Selection with Dijkstra)
**Purpose**: Routes data packets across the global internet
**Real Usage**: ISP routers, CDNs, cloud providers

```pseudocode
╔════════════════════════════════════════════════════════════════════╗
║ ALGORITHM: BGP Best Path Selection with QoS Constraints           ║
║ Scale: 900K+ routes | Convergence: <30s | Updates: 1000/s         ║
╚════════════════════════════════════════════════════════════════════╝

▶ INPUT PARAMETERS:
  routing_table: RoutingTable        # Current BGP routes
  update: BGPUpdate                  # New route advertisement
  local_policies: array[Policy]      # Local routing policies
  network_topology: ASGraph          # Autonomous System graph
  qos_requirements: QoSConstraints   # Latency, bandwidth needs
  
▶ OUTPUT:
  best_path: BGPRoute                # Selected route
  backup_paths: array[BGPRoute]      # Alternative routes
  actions: array[RouteAction]        # Install/withdraw actions

▶ DATA STRUCTURES:
  BGPRoute: {
    prefix: IPPrefix                # Destination network
    next_hop: IPAddress             # Next router
    as_path: array[ASNumber]        # Path through ASes
    local_pref: int                 # Local preference (higher=better)
    med: int                        # Multi-exit discriminator
    origin: enum                    # IGP, EGP, or Incomplete
    communities: array[string]      # Route tags
    weight: int                     # Cisco-specific
  }
  
  ASGraph: {
    nodes: map[ASNumber, ASNode]
    edges: map[pair[AS,AS], ASLink]
  }
  
  ASLink: {
    latency: float                  # Milliseconds
    bandwidth: int                  # Mbps
    packet_loss: float              # Percentage
    cost: float                     # Financial cost
  }

▶ ALGORITHM:
FUNCTION selectBestPath(routing_table, update, policies, topology, qos):
    
    ══════ STEP 1: Validate and Filter Update ══════
    IF NOT validateBGPUpdate(update):
        RETURN NULL  # Invalid update
    
    # Check route filters
    FOR policy IN policies:
        IF policy.type == "IMPORT_FILTER":
            IF NOT policy.matches(update):
                RETURN NULL  # Filtered out
    
    ══════ STEP 2: Find Competing Routes ══════
    prefix ← update.prefix
    existing_routes ← routing_table.getRoutes(prefix)
    candidate_routes ← existing_routes + [update]
    
    # Apply import policies (modify attributes)
    FOR route IN candidate_routes:
        FOR policy IN policies:
            IF policy.type == "ROUTE_MAP":
                applyRouteMap(route, policy)
    
    ══════ STEP 3: BGP Best Path Algorithm ══════
    # Step-by-step elimination
    remaining ← candidate_routes.copy()
    
    # 1. Prefer highest WEIGHT (Cisco-specific)
    IF hasWeight(remaining[0]):
        max_weight ← MAX(route.weight FOR route IN remaining)
        remaining ← [r FOR r IN remaining IF r.weight == max_weight]
    
    IF length(remaining) == 1:
        RETURN remaining[0]
    
    # 2. Prefer highest LOCAL_PREF
    max_local_pref ← MAX(route.local_pref FOR route IN remaining)
    remaining ← [r FOR r IN remaining IF r.local_pref == max_local_pref]
    
    IF length(remaining) == 1:
        RETURN remaining[0]
    
    # 3. Prefer locally originated routes
    local_routes ← [r FOR r IN remaining IF r.next_hop == LOCAL]
    IF length(local_routes) > 0:
        remaining ← local_routes
    
    IF length(remaining) == 1:
        RETURN remaining[0]
    
    # 4. Prefer shortest AS_PATH
    min_path_length ← MIN(length(route.as_path) FOR route IN remaining)
    remaining ← [r FOR r IN remaining IF length(r.as_path) == min_path_length]
    
    IF length(remaining) == 1:
        RETURN remaining[0]
    
    # 5. Prefer lowest ORIGIN (IGP < EGP < Incomplete)
    origin_preference ← {"IGP": 0, "EGP": 1, "Incomplete": 2}
    min_origin ← MIN(origin_preference[route.origin] FOR route IN remaining)
    remaining ← [r FOR r IN remaining IF origin_preference[r.origin] == min_origin]
    
    IF length(remaining) == 1:
        RETURN remaining[0]
    
    # 6. Prefer lowest MED (from same AS)
    grouped_by_as ← groupBy(remaining, lambda r: r.as_path[0])
    remaining_after_med ← []
    
    FOR as_num, routes IN grouped_by_as:
        min_med ← MIN(route.med FOR route IN routes)
        best_from_as ← [r FOR r IN routes IF r.med == min_med]
        remaining_after_med.extend(best_from_as)
    
    remaining ← remaining_after_med
    
    IF length(remaining) == 1:
        RETURN remaining[0]
    
    # 7. Prefer eBGP over iBGP
    ebgp_routes ← [r FOR r IN remaining IF r.peer_type == "eBGP"]
    IF length(ebgp_routes) > 0:
        remaining ← ebgp_routes
    
    IF length(remaining) == 1:
        RETURN remaining[0]
    
    # 8. Prefer path with lowest IGP metric to next hop
    igp_metrics ← {}
    FOR route IN remaining:
        igp_metrics[route] ← getIGPMetric(route.next_hop, topology)
    
    min_igp ← MIN(igp_metrics.values())
    remaining ← [r FOR r IN remaining IF igp_metrics[r] == min_igp]
    
    IF length(remaining) == 1:
        RETURN remaining[0]
    
    ══════ STEP 4: Apply QoS Constraints ══════
    IF qos != NULL:
        qos_viable ← []
        
        FOR route IN remaining:
            path_metrics ← calculatePathMetrics(route, topology)
            
            IF path_metrics.latency <= qos.max_latency AND
               path_metrics.bandwidth >= qos.min_bandwidth AND
               path_metrics.packet_loss <= qos.max_packet_loss:
                qos_viable.append(route)
        
        IF length(qos_viable) > 0:
            remaining ← qos_viable
    
    # 9. Tiebreakers
    IF length(remaining) > 1:
        # Prefer oldest route (stability)
        oldest ← MIN(remaining, key=lambda r: r.received_time)
        RETURN oldest
    
    RETURN remaining[0]
    
    ══════ STEP 5: Find Backup Paths ══════
    FUNCTION findBackupPaths(best_path, all_routes, max_backups=2):
        backups ← []
        
        # Remove best path from candidates
        candidates ← [r FOR r IN all_routes IF r != best_path]
        
        FOR route IN candidates:
            # Check if disjoint enough
            as_overlap ← intersection(route.as_path, best_path.as_path)
            
            IF length(as_overlap) < 0.5 × length(best_path.as_path):
                backups.append(route)
                
                IF length(backups) >= max_backups:
                    BREAK
        
        RETURN backups
    END FUNCTION
END FUNCTION

▶ PATH COMPUTATION WITH DIJKSTRA:
FUNCTION calculatePathMetrics(route, topology):
    # Use Dijkstra to find actual path metrics
    as_path ← route.as_path
    total_latency ← 0
    min_bandwidth ← INFINITY
    max_packet_loss ← 0
    
    FOR i FROM 0 TO length(as_path)-2:
        src_as ← as_path[i]
        dst_as ← as_path[i+1]
        
        link ← topology.getLink(src_as, dst_as)
        
        IF link != NULL:
            total_latency += link.latency
            min_bandwidth ← MIN(min_bandwidth, link.bandwidth)
            max_packet_loss ← MAX(max_packet_loss, link.packet_loss)
        ELSE:
            # Estimate if link data unavailable
            total_latency += estimateLatency(src_as, dst_as)
            min_bandwidth ← MIN(min_bandwidth, 1000)  # Default 1Gbps
    
    RETURN PathMetrics{
        latency: total_latency,
        bandwidth: min_bandwidth,
        packet_loss: max_packet_loss
    }
END FUNCTION

▶ ROUTE INSTALLATION:
FUNCTION installRoute(best_path, routing_table, backup_paths):
    actions ← []
    
    # Check if replacing existing route
    existing ← routing_table.getRoute(best_path.prefix)
    
    IF existing != NULL:
        IF existing != best_path:
            actions.append(RouteAction{
                type: "WITHDRAW",
                route: existing
            })
    
    # Install new route
    actions.append(RouteAction{
        type: "INSTALL",
        route: best_path,
        priority: 0
    })
    
    # Install backup routes with lower priority
    FOR i, backup IN enumerate(backup_paths):
        actions.append(RouteAction{
            type: "INSTALL",
            route: backup,
            priority: i + 1
        })
    
    # Update FIB (Forwarding Information Base)
    FOR action IN actions:
        IF action.type == "INSTALL":
            routing_table.fib.insert(
                action.route.prefix,
                action.route.next_hop,
                action.priority
            )
        ELSE IF action.type == "WITHDRAW":
            routing_table.fib.remove(
                action.route.prefix,
                action.route.next_hop
            )
    
    RETURN actions
END FUNCTION

▶ CONVERGENCE OPTIMIZATION:
FUNCTION optimizeBGPConvergence(routing_table, updates):
    # Batch processing for faster convergence
    updates_by_prefix ← groupBy(updates, lambda u: u.prefix)
    
    # Process withdrawals first (avoid loops)
    FOR prefix, prefix_updates IN updates_by_prefix:
        withdrawals ← [u FOR u IN prefix_updates IF u.type == "WITHDRAW"]
        FOR withdrawal IN withdrawals:
            routing_table.remove(withdrawal)
    
    # Then process announcements
    FOR prefix, prefix_updates IN updates_by_prefix:
        announcements ← [u FOR u IN prefix_updates IF u.type == "ANNOUNCE"]
        
        IF length(announcements) > 0:
            # Only run selection once per prefix
            best ← selectBestPath(routing_table, announcements, ...)
            installRoute(best, routing_table, ...)
    
    # MRAI timer (Min Route Advertisement Interval)
    scheduleTimer(30, sendUpdates)  # Batch outgoing updates
END FUNCTION

▶ OPTIMIZATIONS:
  • Route aggregation to reduce table size
  • Incremental SPF for topology changes
  • Path caching for common destinations
  • Parallel route processing
  • Bloom filters for loop detection
  • Fast reroute with pre-computed backups
```

## Summary

These search algorithms power critical infrastructure across the internet and modern applications:

1. **Web Search**: PageRank + inverted indexes enable sub-second searches across billions of pages
2. **GPS Navigation**: A* with traffic data routes millions of drivers in real-time
3. **Databases**: B+ trees provide logarithmic search in tables with billions of rows
4. **Image Search**: KD-trees and SIFT features power visual search engines
5. **Game AI**: Jump Point Search enables real-time pathfinding for thousands of units
6. **File Search**: Boyer-Moore achieves GB/s search speeds in text files
7. **Similarity Search**: LSH finds similar items in high-dimensional spaces efficiently
8. **Network Routing**: BGP and Dijkstra route internet traffic globally

Each algorithm is optimized for its specific domain, demonstrating how search is fundamental to modern computing infrastructure.