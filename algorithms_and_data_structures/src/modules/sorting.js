/**
 * Sorting: Organizing Music Playlists
 * 
 * Just like organizing your music collection by different criteria
 * (artist, genre, release date), sorting algorithms arrange data in order.
 */

class Song {
  constructor(title, artist, album, genre, year, duration, rating = 0) {
    this.title = title;
    this.artist = artist;
    this.album = album;
    this.genre = genre;
    this.year = year;
    this.duration = duration; // in seconds
    this.rating = rating; // 1-5 stars
    this.playCount = 0;
    this.id = Math.random().toString(36).substr(2, 9);
  }

  formatDuration() {
    const minutes = Math.floor(this.duration / 60);
    const seconds = this.duration % 60;
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  }

  play() {
    this.playCount++;
    console.log(`🎵 Now playing: ${this.title} by ${this.artist}`);
  }

  toString() {
    return `"${this.title}" by ${this.artist} (${this.year}) - ${this.formatDuration()} [🌟${this.rating}]`;
  }
}

class MusicPlaylist {
  constructor(name = 'My Playlist') {
    this.name = name;
    this.songs = [];
    this.sortHistory = [];
  }

  /**
   * Add song to playlist
   */
  addSong(title, artist, album, genre, year, duration, rating = 0) {
    const song = new Song(title, artist, album, genre, year, duration, rating);
    this.songs.push(song);
    console.log(`➕ Added "${title}" to ${this.name}`);
    return song;
  }

  /**
   * Display current playlist
   */
  displayPlaylist() {
    console.log(`\n🎵 ${this.name} (${this.songs.length} songs):`);
    console.log('----------------------------------------');
    
    if (this.songs.length === 0) {
      console.log('Empty playlist');
      return;
    }
    
    this.songs.forEach((song, index) => {
      console.log(`${(index + 1).toString().padStart(2)}. ${song.toString()}`);
    });
    
    const totalDuration = this.songs.reduce((sum, song) => sum + song.duration, 0);
    console.log(`\nTotal duration: ${Math.floor(totalDuration / 60)} minutes`);
  }

  /**
   * Bubble Sort: Simple but inefficient (like organizing CDs one by one)
   * Time Complexity: O(n²), Space: O(1)
   */
  bubbleSortByTitle() {
    console.log('\n🧭 Bubble Sort by Title (comparing adjacent songs):');
    
    const n = this.songs.length;
    let swapped;
    let comparisons = 0;
    let swaps = 0;
    
    for (let i = 0; i < n - 1; i++) {
      swapped = false;
      
      for (let j = 0; j < n - i - 1; j++) {
        comparisons++;
        
        if (this.songs[j].title > this.songs[j + 1].title) {
          // Swap songs
          [this.songs[j], this.songs[j + 1]] = [this.songs[j + 1], this.songs[j]];
          swapped = true;
          swaps++;
          
          console.log(`  Swapped "${this.songs[j + 1].title}" with "${this.songs[j].title}"`);
        }
      }
      
      if (!swapped) {
        console.log('  No more swaps needed - list is sorted!');
        break;
      }
    }
    
    console.log(`✅ Bubble sort complete: ${comparisons} comparisons, ${swaps} swaps`);
    this.sortHistory.push({ method: 'Bubble Sort', criteria: 'Title', comparisons, swaps });
  }

  /**
   * Quick Sort: Efficient divide-and-conquer (like organizing by picking a reference song)
   * Time Complexity: O(n log n) average, O(n²) worst case, Space: O(log n)
   */
  quickSortByYear() {
    console.log('\n⚡ Quick Sort by Year (divide and conquer):');
    
    let comparisons = 0;
    let swaps = 0;
    
    const quickSort = (arr, low, high) => {
      if (low < high) {
        const pivotIndex = partition(arr, low, high);
        quickSort(arr, low, pivotIndex - 1);
        quickSort(arr, pivotIndex + 1, high);
      }
    };
    
    const partition = (arr, low, high) => {
      const pivot = arr[high].year;
      console.log(`  Using pivot: ${arr[high].title} (${pivot})`);
      
      let i = low - 1;
      
      for (let j = low; j < high; j++) {
        comparisons++;
        
        if (arr[j].year <= pivot) {
          i++;
          if (i !== j) {
            [arr[i], arr[j]] = [arr[j], arr[i]];
            swaps++;
            console.log(`    Moved "${arr[j].title}" before pivot`);
          }
        }
      }
      
      [arr[i + 1], arr[high]] = [arr[high], arr[i + 1]];
      swaps++;
      
      return i + 1;
    };
    
    quickSort(this.songs, 0, this.songs.length - 1);
    
    console.log(`✅ Quick sort complete: ${comparisons} comparisons, ${swaps} swaps`);
    this.sortHistory.push({ method: 'Quick Sort', criteria: 'Year', comparisons, swaps });
  }

  /**
   * Merge Sort: Stable and consistent (like merging two pre-sorted playlists)
   * Time Complexity: O(n log n), Space: O(n)
   */
  mergeSortByArtist() {
    console.log('\n🔄 Merge Sort by Artist (divide and merge):');
    
    let comparisons = 0;
    let merges = 0;
    
    const mergeSort = (arr) => {
      if (arr.length <= 1) return arr;
      
      const mid = Math.floor(arr.length / 2);
      const left = arr.slice(0, mid);
      const right = arr.slice(mid);
      
      console.log(`  Dividing: [${left.length} songs] | [${right.length} songs]`);
      
      return merge(mergeSort(left), mergeSort(right));
    };
    
    const merge = (left, right) => {
      const result = [];
      let leftIndex = 0;
      let rightIndex = 0;
      
      while (leftIndex < left.length && rightIndex < right.length) {
        comparisons++;
        
        if (left[leftIndex].artist <= right[rightIndex].artist) {
          result.push(left[leftIndex]);
          leftIndex++;
        } else {
          result.push(right[rightIndex]);
          rightIndex++;
        }
      }
      
      // Add remaining songs
      result.push(...left.slice(leftIndex));
      result.push(...right.slice(rightIndex));
      
      merges++;
      console.log(`  Merged ${result.length} songs`);
      
      return result;
    };
    
    this.songs = mergeSort(this.songs);
    
    console.log(`✅ Merge sort complete: ${comparisons} comparisons, ${merges} merge operations`);
    this.sortHistory.push({ method: 'Merge Sort', criteria: 'Artist', comparisons, merges });
  }

  /**
   * Heap Sort: Using a priority queue (like top charts)
   * Time Complexity: O(n log n), Space: O(1)
   */
  heapSortByRating() {
    console.log('\n🗺️  Heap Sort by Rating (building a priority queue):');
    
    let comparisons = 0;
    let swaps = 0;
    
    const heapify = (arr, n, rootIndex) => {
      let largest = rootIndex;
      const left = 2 * rootIndex + 1;
      const right = 2 * rootIndex + 2;
      
      if (left < n) {
        comparisons++;
        if (arr[left].rating > arr[largest].rating) {
          largest = left;
        }
      }
      
      if (right < n) {
        comparisons++;
        if (arr[right].rating > arr[largest].rating) {
          largest = right;
        }
      }
      
      if (largest !== rootIndex) {
        [arr[rootIndex], arr[largest]] = [arr[largest], arr[rootIndex]];
        swaps++;
        console.log(`  Heapified: moved "${arr[largest].title}" down`);
        heapify(arr, n, largest);
      }
    };
    
    const n = this.songs.length;
    
    // Build max heap
    console.log('  Building max heap...');
    for (let i = Math.floor(n / 2) - 1; i >= 0; i--) {
      heapify(this.songs, n, i);
    }
    
    // Extract elements from heap
    console.log('  Extracting sorted elements...');
    for (let i = n - 1; i > 0; i--) {
      [this.songs[0], this.songs[i]] = [this.songs[i], this.songs[0]];
      swaps++;
      
      console.log(`  Extracted: "${this.songs[i].title}" (rating: ${this.songs[i].rating})`);
      heapify(this.songs, i, 0);
    }
    
    console.log(`✅ Heap sort complete: ${comparisons} comparisons, ${swaps} swaps`);
    this.sortHistory.push({ method: 'Heap Sort', criteria: 'Rating', comparisons, swaps });
  }

  /**
   * Insertion Sort: Good for small lists (like sorting new songs into existing order)
   * Time Complexity: O(n²) worst case, O(n) best case, Space: O(1)
   */
  insertionSortByDuration() {
    console.log('\n➡️  Insertion Sort by Duration (inserting each song in correct position):');
    
    let comparisons = 0;
    let shifts = 0;
    
    for (let i = 1; i < this.songs.length; i++) {
      const currentSong = this.songs[i];
      let j = i - 1;
      
      console.log(`  Inserting: "${currentSong.title}" (${currentSong.formatDuration()})`);
      
      while (j >= 0) {
        comparisons++;
        
        if (this.songs[j].duration <= currentSong.duration) {
          break;
        }
        
        this.songs[j + 1] = this.songs[j];
        shifts++;
        j--;
      }
      
      this.songs[j + 1] = currentSong;
      
      if (j + 1 !== i) {
        console.log(`    Inserted at position ${j + 2}`);
      }
    }
    
    console.log(`✅ Insertion sort complete: ${comparisons} comparisons, ${shifts} shifts`);
    this.sortHistory.push({ method: 'Insertion Sort', criteria: 'Duration', comparisons, shifts });
  }

  /**
   * Selection Sort: Find and place (like picking the best song each time)
   * Time Complexity: O(n²), Space: O(1)
   */
  selectionSortByPlayCount() {
    console.log('\n🎯 Selection Sort by Play Count (finding best each time):');
    
    let comparisons = 0;
    let swaps = 0;
    
    for (let i = 0; i < this.songs.length - 1; i++) {
      let maxIndex = i;
      
      // Find song with highest play count in remaining unsorted portion
      for (let j = i + 1; j < this.songs.length; j++) {
        comparisons++;
        
        if (this.songs[j].playCount > this.songs[maxIndex].playCount) {
          maxIndex = j;
        }
      }
      
      if (maxIndex !== i) {
        [this.songs[i], this.songs[maxIndex]] = [this.songs[maxIndex], this.songs[i]];
        swaps++;
        
        console.log(`  Selected: "${this.songs[i].title}" (${this.songs[i].playCount} plays)`);
      }
    }
    
    console.log(`✅ Selection sort complete: ${comparisons} comparisons, ${swaps} swaps`);
    this.sortHistory.push({ method: 'Selection Sort', criteria: 'Play Count', comparisons, swaps });
  }

  /**
   * Counting Sort: For limited range values (like ratings 1-5)
   * Time Complexity: O(n + k) where k is range, Space: O(k)
   */
  countingSortByRating() {
    console.log('\n📊 Counting Sort by Rating (histogram approach):');
    
    const maxRating = 5;
    const count = new Array(maxRating + 1).fill(0);
    
    // Count occurrences
    console.log('  Counting ratings...');
    for (const song of this.songs) {
      count[song.rating]++;
    }
    
    // Display histogram
    for (let i = 0; i <= maxRating; i++) {
      if (count[i] > 0) {
        console.log(`    ${i} stars: ${count[i]} songs`);
      }
    }
    
    // Transform count array to position array
    for (let i = 1; i <= maxRating; i++) {
      count[i] += count[i - 1];
    }
    
    // Build sorted array
    const sorted = new Array(this.songs.length);
    for (let i = this.songs.length - 1; i >= 0; i--) {
      const rating = this.songs[i].rating;
      sorted[count[rating] - 1] = this.songs[i];
      count[rating]--;
    }
    
    this.songs = sorted;
    
    console.log('✅ Counting sort complete: O(n + k) time complexity');
    this.sortHistory.push({ method: 'Counting Sort', criteria: 'Rating', timeComplexity: 'O(n + k)' });
  }

  /**
   * Radix Sort: For numerical data (like year)
   * Time Complexity: O(d * n) where d is number of digits
   */
  radixSortByYear() {
    console.log('\n🔢 Radix Sort by Year (digit by digit):');
    
    const getMax = (arr) => {
      return Math.max(...arr.map(song => song.year));
    };
    
    const countingSortByDigit = (arr, exp) => {
      const count = new Array(10).fill(0);
      const output = new Array(arr.length);
      
      // Count occurrences of each digit
      for (const song of arr) {
        const digit = Math.floor(song.year / exp) % 10;
        count[digit]++;
      }
      
      console.log(`  Processing digit at position ${Math.log10(exp) + 1}`);
      
      // Transform count array
      for (let i = 1; i < 10; i++) {
        count[i] += count[i - 1];
      }
      
      // Build output array
      for (let i = arr.length - 1; i >= 0; i--) {
        const digit = Math.floor(arr[i].year / exp) % 10;
        output[count[digit] - 1] = arr[i];
        count[digit]--;
      }
      
      return output;
    };
    
    const max = getMax(this.songs);
    
    // Do counting sort for every digit
    for (let exp = 1; Math.floor(max / exp) > 0; exp *= 10) {
      this.songs = countingSortByDigit(this.songs, exp);
    }
    
    console.log('✅ Radix sort complete: sorted by each digit position');
    this.sortHistory.push({ method: 'Radix Sort', criteria: 'Year', timeComplexity: 'O(d * n)' });
  }

  /**
   * Multi-criteria sorting (like Spotify's complex ranking)
   */
  multiCriteriaSort(primaryCriteria = 'rating', secondaryCriteria = 'playCount') {
    console.log(`\n🎼 Multi-criteria Sort: ${primaryCriteria} then ${secondaryCriteria}`);
    
    this.songs.sort((a, b) => {
      // Primary sort
      if (a[primaryCriteria] !== b[primaryCriteria]) {
        return b[primaryCriteria] - a[primaryCriteria]; // Descending
      }
      
      // Secondary sort if primary is equal
      return b[secondaryCriteria] - a[secondaryCriteria]; // Descending
    });
    
    console.log('✅ Multi-criteria sort complete');
    this.sortHistory.push({ 
      method: 'Multi-criteria Sort', 
      criteria: `${primaryCriteria} + ${secondaryCriteria}` 
    });
  }

  /**
   * Shuffle playlist (Fisher-Yates algorithm)
   */
  shuffle() {
    console.log('\n🎲 Shuffling playlist (Fisher-Yates algorithm):');
    
    for (let i = this.songs.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [this.songs[i], this.songs[j]] = [this.songs[j], this.songs[i]];
      
      console.log(`  Swapped positions ${i + 1} and ${j + 1}`);
    }
    
    console.log('✅ Playlist shuffled randomly');
  }

  /**
   * Display sorting performance history
   */
  displaySortingHistory() {
    console.log('\n📈 Sorting Performance History:');
    console.log('Method\t\tCriteria\tComparisons\tSwaps/Operations');
    console.log('----------------------------------------------------------------');
    
    this.sortHistory.forEach(sort => {
      const operations = sort.swaps || sort.merges || 'N/A';
      console.log(`${sort.method.padEnd(15)}\t${sort.criteria.padEnd(12)}\t${(sort.comparisons || 'N/A').toString().padEnd(12)}\t${operations}`);
    });
  }

  /**
   * Create themed playlists
   */
  createThemedPlaylist(theme) {
    console.log(`\n🎵 Creating ${theme} playlist:`);
    
    let filteredSongs = [];
    
    switch (theme.toLowerCase()) {
      case 'top rated':
        filteredSongs = this.songs.filter(song => song.rating >= 4);
        break;
      case 'recent':
        filteredSongs = this.songs.filter(song => song.year >= 2020);
        break;
      case 'classics':
        filteredSongs = this.songs.filter(song => song.year < 2000);
        break;
      case 'popular':
        filteredSongs = this.songs.filter(song => song.playCount > 5);
        break;
      default:
        filteredSongs = this.songs.filter(song => 
          song.genre.toLowerCase().includes(theme.toLowerCase())
        );
    }
    
    const themedPlaylist = new MusicPlaylist(`${theme} Playlist`);
    filteredSongs.forEach(song => {
      themedPlaylist.songs.push(song);
    });
    
    console.log(`Created playlist with ${filteredSongs.length} songs`);
    return themedPlaylist;
  }

  /**
   * Real-world applications demonstration
   */
  static demonstrateApplications() {
    console.log(`\n🌟 Real-World Applications of Sorting:\n\n` +
      `1. 📊 Database Indexing: Faster data retrieval\n` +
      `2. 🔍 Search Engines: Ranking search results\n` +
      `3. 🎮 Game Leaderboards: Player rankings\n` +
      `4. 📦 E-commerce: Product sorting by price, rating\n` +
      `5. 📱 Contact Lists: Alphabetical organization\n` +
      `6. 📰 News Feeds: Chronological or priority order\n` +
      `7. 📦 Logistics: Route optimization\n`);
  }
}

/**
 * Sorting Practice Problems
 */
class SortingPracticeProblems {
  /**
   * Problem 1: Find kth largest element (QuickSelect)
   */
  static findKthLargest(playlist, k) {
    console.log(`🏆 Finding ${k}th most popular song:`);
    
    const songs = [...playlist.songs]; // Copy array
    
    const quickSelect = (arr, left, right, k) => {
      if (left === right) return arr[left];
      
      const pivotIndex = partition(arr, left, right);
      
      if (k === pivotIndex) {
        return arr[k];
      } else if (k < pivotIndex) {
        return quickSelect(arr, left, pivotIndex - 1, k);
      } else {
        return quickSelect(arr, pivotIndex + 1, right, k);
      }
    };
    
    const partition = (arr, left, right) => {
      const pivot = arr[right].playCount;
      let i = left - 1;
      
      for (let j = left; j < right; j++) {
        if (arr[j].playCount >= pivot) {
          i++;
          [arr[i], arr[j]] = [arr[j], arr[i]];
        }
      }
      
      [arr[i + 1], arr[right]] = [arr[right], arr[i + 1]];
      return i + 1;
    };
    
    const kthSong = quickSelect(songs, 0, songs.length - 1, k - 1);
    console.log(`  ${k}th most popular: "${kthSong.title}" (${kthSong.playCount} plays)`);
    
    return kthSong;
  }

  /**
   * Problem 2: Merge k sorted playlists
   */
  static mergeKSortedPlaylists(playlists) {
    console.log(`🔄 Merging ${playlists.length} sorted playlists:`);
    
    const merged = new MusicPlaylist('Merged Playlist');
    const heap = []; // Min heap of {song, playlistIndex, songIndex}
    
    // Initialize heap with first song from each playlist
    playlists.forEach((playlist, playlistIndex) => {
      if (playlist.songs.length > 0) {
        heap.push({
          song: playlist.songs[0],
          playlistIndex,
          songIndex: 0
        });
      }
    });
    
    // Simple heap operations (in real implementation, use proper heap)
    while (heap.length > 0) {
      // Find minimum (should use proper heap extract-min)
      let minIndex = 0;
      for (let i = 1; i < heap.length; i++) {
        if (heap[i].song.title < heap[minIndex].song.title) {
          minIndex = i;
        }
      }
      
      const minElement = heap.splice(minIndex, 1)[0];
      merged.songs.push(minElement.song);
      
      // Add next song from same playlist
      const nextSongIndex = minElement.songIndex + 1;
      const playlist = playlists[minElement.playlistIndex];
      
      if (nextSongIndex < playlist.songs.length) {
        heap.push({
          song: playlist.songs[nextSongIndex],
          playlistIndex: minElement.playlistIndex,
          songIndex: nextSongIndex
        });
      }
    }
    
    console.log(`  Merged ${merged.songs.length} songs from ${playlists.length} playlists`);
    return merged;
  }

  /**
   * Problem 3: Sort songs by custom criteria
   */
  static customSort(playlist, weightRating = 0.4, weightPlayCount = 0.3, weightYear = 0.3) {
    console.log('\n🎯 Custom Weighted Sort:');
    console.log(`  Weights: Rating(${weightRating}), PlayCount(${weightPlayCount}), Year(${weightYear})`);
    
    playlist.songs.sort((a, b) => {
      const scoreA = (a.rating / 5) * weightRating + 
                    (a.playCount / 100) * weightPlayCount + 
                    ((a.year - 1950) / 70) * weightYear;
      
      const scoreB = (b.rating / 5) * weightRating + 
                    (b.playCount / 100) * weightPlayCount + 
                    ((b.year - 1950) / 70) * weightYear;
      
      return scoreB - scoreA; // Descending
    });
    
    console.log('  Custom sort complete - songs ranked by weighted score');
  }

  /**
   * Problem 4: Find duplicate songs
   */
  static findDuplicates(playlist) {
    console.log('\n🔍 Finding duplicate songs:');
    
    const seen = new Map();
    const duplicates = [];
    
    for (const song of playlist.songs) {
      const key = `${song.title.toLowerCase()}-${song.artist.toLowerCase()}`;
      
      if (seen.has(key)) {
        duplicates.push(song);
        console.log(`  Duplicate found: "${song.title}" by ${song.artist}`);
      } else {
        seen.set(key, song);
      }
    }
    
    console.log(`  Found ${duplicates.length} duplicate songs`);
    return duplicates;
  }
}

// Export for use in other modules
export { 
  Song, 
  MusicPlaylist, 
  SortingPracticeProblems 
};

// Example usage and demonstration
import { fileURLToPath } from 'url';
import { argv } from 'process';
const __filename = fileURLToPath(import.meta.url);

if (argv[1] === __filename) {
  console.log('🎵 Welcome to the Music Playlist Sorting Learning Module!\n');
  
  // Create playlist and add songs
  const myPlaylist = new MusicPlaylist('Ultimate Mix');
  
  console.log('🎵 Adding songs to playlist:');
  myPlaylist.addSong('Bohemian Rhapsody', 'Queen', 'A Night at the Opera', 'Rock', 1975, 355, 5);
  myPlaylist.addSong('Hotel California', 'Eagles', 'Hotel California', 'Rock', 1976, 391, 5);
  myPlaylist.addSong('Billie Jean', 'Michael Jackson', 'Thriller', 'Pop', 1983, 294, 5);
  myPlaylist.addSong('Smells Like Teen Spirit', 'Nirvana', 'Nevermind', 'Grunge', 1991, 301, 4);
  myPlaylist.addSong('Wonderwall', 'Oasis', '(What\'s the Story) Morning Glory?', 'Britpop', 1995, 258, 4);
  myPlaylist.addSong('Shape of You', 'Ed Sheeran', '÷', 'Pop', 2017, 233, 3);
  myPlaylist.addSong('Blinding Lights', 'The Weeknd', 'After Hours', 'Pop', 2020, 200, 4);
  myPlaylist.addSong('Someone Like You', 'Adele', '21', 'Pop', 2011, 285, 4);
  
  // Simulate some play counts
  myPlaylist.songs[0].playCount = 25; // Bohemian Rhapsody
  myPlaylist.songs[1].playCount = 18; // Hotel California
  myPlaylist.songs[2].playCount = 30; // Billie Jean
  myPlaylist.songs[3].playCount = 15; // Teen Spirit
  myPlaylist.songs[4].playCount = 12; // Wonderwall
  myPlaylist.songs[5].playCount = 22; // Shape of You
  myPlaylist.songs[6].playCount = 28; // Blinding Lights
  myPlaylist.songs[7].playCount = 20; // Someone Like You
  
  myPlaylist.displayPlaylist();
  
  // Demonstrate different sorting algorithms
  console.log('\n📊 Sorting Algorithm Demonstrations:');
  
  // 1. Bubble Sort
  const bubblePlaylist = new MusicPlaylist('Bubble Sorted');
  bubblePlaylist.songs = [...myPlaylist.songs];
  bubblePlaylist.bubbleSortByTitle();
  
  // 2. Quick Sort
  const quickPlaylist = new MusicPlaylist('Quick Sorted');
  quickPlaylist.songs = [...myPlaylist.songs];
  quickPlaylist.quickSortByYear();
  
  // 3. Merge Sort
  const mergePlaylist = new MusicPlaylist('Merge Sorted');
  mergePlaylist.songs = [...myPlaylist.songs];
  mergePlaylist.mergeSortByArtist();
  
  // 4. Heap Sort
  const heapPlaylist = new MusicPlaylist('Heap Sorted');
  heapPlaylist.songs = [...myPlaylist.songs];
  heapPlaylist.heapSortByRating();
  
  // 5. Insertion Sort
  const insertionPlaylist = new MusicPlaylist('Insertion Sorted');
  insertionPlaylist.songs = [...myPlaylist.songs];
  insertionPlaylist.insertionSortByDuration();
  
  // 6. Selection Sort
  const selectionPlaylist = new MusicPlaylist('Selection Sorted');
  selectionPlaylist.songs = [...myPlaylist.songs];
  selectionPlaylist.selectionSortByPlayCount();
  
  // 7. Counting Sort
  const countingPlaylist = new MusicPlaylist('Counting Sorted');
  countingPlaylist.songs = [...myPlaylist.songs];
  countingPlaylist.countingSortByRating();
  
  // 8. Multi-criteria Sort
  const multiPlaylist = new MusicPlaylist('Multi-Criteria Sorted');
  multiPlaylist.songs = [...myPlaylist.songs];
  multiPlaylist.multiCriteriaSort('rating', 'playCount');
  multiPlaylist.displayPlaylist();
  
  // Display sorting performance comparison
  console.log('\n📊 Sorting Performance Comparison:');
  bubblePlaylist.displaySortingHistory();
  
  // Demonstrate shuffle
  console.log('\n🎲 Shuffle demonstration:');
  const shufflePlaylist = new MusicPlaylist('Shuffled');
  shufflePlaylist.songs = [...myPlaylist.songs];
  shufflePlaylist.shuffle();
  
  // Create themed playlists
  console.log('\n🎵 Themed Playlists:');
  const topRated = myPlaylist.createThemedPlaylist('Top Rated');
  topRated.displayPlaylist();
  
  const rockPlaylist = myPlaylist.createThemedPlaylist('Rock');
  rockPlaylist.displayPlaylist();
  
  // Show real-world applications
  MusicPlaylist.demonstrateApplications();
  
  // Practice problems
  console.log('\n🧠 Sorting Practice Problems:');
  
  console.log('\n1. Find Kth Largest:');
  SortingPracticeProblems.findKthLargest(myPlaylist, 3);
  
  console.log('\n2. Custom Weighted Sort:');
  SortingPracticeProblems.customSort(myPlaylist, 0.5, 0.3, 0.2);
  
  console.log('\n3. Find Duplicates:');
  // Add a duplicate for testing
  myPlaylist.addSong('Hotel California', 'Eagles', 'Hell Freezes Over', 'Rock', 1994, 395, 5);
  SortingPracticeProblems.findDuplicates(myPlaylist);
}