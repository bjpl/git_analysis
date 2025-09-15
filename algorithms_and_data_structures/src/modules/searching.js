/**
 * Searching: Finding a Contact in Your Phone
 * 
 * Just like searching through your phone's contact list to find someone,
 * searching algorithms help us locate specific data efficiently.
 */

class Contact {
  constructor(name, phone, email, category = 'personal', favorite = false) {
    this.name = name;
    this.phone = phone;
    this.email = email;
    this.category = category; // personal, work, family, etc.
    this.favorite = favorite;
    this.lastCalled = null;
    this.callCount = 0;
    this.id = Math.random().toString(36).substr(2, 9);
    this.addedDate = new Date();
  }

  call() {
    this.lastCalled = new Date();
    this.callCount++;
    console.log(`📞 Calling ${this.name} at ${this.phone}`);
  }

  toString() {
    const favoriteIcon = this.favorite ? '⭐' : '';
    return `${favoriteIcon}${this.name} - ${this.phone} (${this.category})`;
  }
}

class PhoneContactBook {
  constructor(ownerName = 'My Phone') {
    this.contacts = [];
    this.ownerName = ownerName;
    this.searchHistory = [];
    this.isSorted = false;
    this.sortedBy = null;
  }

  /**
   * Add contact to phone book
   */
  addContact(name, phone, email, category = 'personal', favorite = false) {
    // Check for duplicates
    const existing = this.contacts.find(c => c.name === name || c.phone === phone);
    if (existing) {
      console.log(`⚠️  Contact already exists: ${existing.name}`);
      return false;
    }
    
    const contact = new Contact(name, phone, email, category, favorite);
    this.contacts.push(contact);
    this.isSorted = false; // Adding new contact breaks sort order
    
    console.log(`➕ Added ${name} to contacts`);
    return contact;
  }

  /**
   * Linear Search: Search through contacts one by one
   * Time Complexity: O(n)
   * Space Complexity: O(1)
   */
  linearSearchByName(searchName) {
    console.log(`\n🔍 Linear Search for "${searchName}":`);
    
    let comparisons = 0;
    const startTime = Date.now();
    
    for (let i = 0; i < this.contacts.length; i++) {
      comparisons++;
      console.log(`  Checking contact ${i + 1}: ${this.contacts[i].name}`);
      
      if (this.contacts[i].name.toLowerCase() === searchName.toLowerCase()) {
        const endTime = Date.now();
        console.log(`✅ Found "${searchName}" at position ${i + 1} after ${comparisons} comparisons (${endTime - startTime}ms)`);
        
        this.searchHistory.push({
          method: 'Linear Search',
          query: searchName,
          found: true,
          comparisons,
          timeMs: endTime - startTime
        });
        
        return this.contacts[i];
      }
    }
    
    const endTime = Date.now();
    console.log(`❌ "${searchName}" not found after ${comparisons} comparisons (${endTime - startTime}ms)`);
    
    this.searchHistory.push({
      method: 'Linear Search',
      query: searchName,
      found: false,
      comparisons,
      timeMs: endTime - startTime
    });
    
    return null;
  }

  /**
   * Binary Search: Search in sorted list (much faster!)
   * Time Complexity: O(log n)
   * Space Complexity: O(1)
   */
  binarySearchByName(searchName) {
    console.log(`\n🎯 Binary Search for "${searchName}":`);
    
    // First, ensure contacts are sorted
    if (!this.isSorted || this.sortedBy !== 'name') {
      console.log('  Contacts not sorted by name - sorting first...');
      this.sortContactsByName();
    }
    
    let left = 0;
    let right = this.contacts.length - 1;
    let comparisons = 0;
    const startTime = Date.now();
    
    while (left <= right) {
      comparisons++;
      const mid = Math.floor((left + right) / 2);
      const midContact = this.contacts[mid];
      
      console.log(`  Checking middle contact (pos ${mid + 1}): ${midContact.name}`);
      
      const comparison = midContact.name.toLowerCase().localeCompare(searchName.toLowerCase());
      
      if (comparison === 0) {
        const endTime = Date.now();
        console.log(`✅ Found "${searchName}" at position ${mid + 1} after ${comparisons} comparisons (${endTime - startTime}ms)`);
        
        this.searchHistory.push({
          method: 'Binary Search',
          query: searchName,
          found: true,
          comparisons,
          timeMs: endTime - startTime
        });
        
        return midContact;
      } else if (comparison > 0) {
        console.log(`    "${midContact.name}" > "${searchName}" - searching left half`);
        right = mid - 1;
      } else {
        console.log(`    "${midContact.name}" < "${searchName}" - searching right half`);
        left = mid + 1;
      }
    }
    
    const endTime = Date.now();
    console.log(`❌ "${searchName}" not found after ${comparisons} comparisons (${endTime - startTime}ms)`);
    
    this.searchHistory.push({
      method: 'Binary Search',
      query: searchName,
      found: false,
      comparisons,
      timeMs: endTime - startTime
    });
    
    return null;
  }

  /**
   * Jump Search: Jump through blocks, then linear search within block
   * Time Complexity: O(√n)
   * Space Complexity: O(1)
   */
  jumpSearchByName(searchName) {
    console.log(`\n🤘 Jump Search for "${searchName}":`);
    
    if (!this.isSorted || this.sortedBy !== 'name') {
      console.log('  Contacts not sorted by name - sorting first...');
      this.sortContactsByName();
    }
    
    const n = this.contacts.length;
    const jumpSize = Math.floor(Math.sqrt(n));
    let prev = 0;
    let comparisons = 0;
    const startTime = Date.now();
    
    console.log(`  Jump size: ${jumpSize}`);
    
    // Jump through blocks
    while (this.contacts[Math.min(jumpSize, n) - 1].name.toLowerCase() < searchName.toLowerCase()) {
      comparisons++;
      console.log(`  Jumped to position ${Math.min(jumpSize, n)}: ${this.contacts[Math.min(jumpSize, n) - 1].name}`);
      
      prev = jumpSize;
      jumpSize += Math.floor(Math.sqrt(n));
      
      if (prev >= n) {
        const endTime = Date.now();
        console.log(`❌ "${searchName}" not found after ${comparisons} comparisons`);
        return null;
      }
    }
    
    // Linear search within the block
    console.log(`  Searching linearly from position ${prev + 1} to ${Math.min(jumpSize, n)}`);
    
    while (prev < Math.min(jumpSize, n)) {
      comparisons++;
      
      if (this.contacts[prev].name.toLowerCase() === searchName.toLowerCase()) {
        const endTime = Date.now();
        console.log(`✅ Found "${searchName}" at position ${prev + 1} after ${comparisons} comparisons (${endTime - startTime}ms)`);
        
        this.searchHistory.push({
          method: 'Jump Search',
          query: searchName,
          found: true,
          comparisons,
          timeMs: endTime - startTime
        });
        
        return this.contacts[prev];
      }
      
      prev++;
    }
    
    const endTime = Date.now();
    console.log(`❌ "${searchName}" not found after ${comparisons} comparisons (${endTime - startTime}ms)`);
    
    this.searchHistory.push({
      method: 'Jump Search',
      query: searchName,
      found: false,
      comparisons,
      timeMs: endTime - startTime
    });
    
    return null;
  }

  /**
   * Exponential Search: Find range then binary search
   * Time Complexity: O(log n)
   * Space Complexity: O(1)
   */
  exponentialSearchByName(searchName) {
    console.log(`\n💥 Exponential Search for "${searchName}":`);
    
    if (!this.isSorted || this.sortedBy !== 'name') {
      this.sortContactsByName();
    }
    
    const n = this.contacts.length;
    let comparisons = 0;
    const startTime = Date.now();
    
    // If first element matches
    if (this.contacts[0].name.toLowerCase() === searchName.toLowerCase()) {
      console.log(`✅ Found "${searchName}" at position 1`);
      return this.contacts[0];
    }
    
    // Find range for binary search by exponential jumps
    let bound = 1;
    while (bound < n && this.contacts[bound].name.toLowerCase() <= searchName.toLowerCase()) {
      comparisons++;
      console.log(`  Checking bound ${bound + 1}: ${this.contacts[bound].name}`);
      bound *= 2;
    }
    
    console.log(`  Range found: positions ${bound / 2 + 1} to ${Math.min(bound + 1, n)}`);
    
    // Binary search within the range
    const result = this.binarySearchInRange(searchName, Math.floor(bound / 2), Math.min(bound, n - 1));
    
    const endTime = Date.now();
    this.searchHistory.push({
      method: 'Exponential Search',
      query: searchName,
      found: result !== null,
      comparisons: comparisons + (result ? 1 : 0),
      timeMs: endTime - startTime
    });
    
    return result;
  }

  /**
   * Interpolation Search: Estimate position based on value
   * Works well with uniformly distributed data
   * Time Complexity: O(log log n) best case, O(n) worst case
   */
  interpolationSearchByPhone(searchPhone) {
    console.log(`\n📱 Interpolation Search for phone "${searchPhone}":`);
    
    // Sort by phone numbers first (treating as strings)
    if (!this.isSorted || this.sortedBy !== 'phone') {
      console.log('  Contacts not sorted by phone - sorting first...');
      this.sortContactsByPhone();
    }
    
    let low = 0;
    let high = this.contacts.length - 1;
    let comparisons = 0;
    const startTime = Date.now();
    
    while (low <= high && 
           searchPhone >= this.contacts[low].phone && 
           searchPhone <= this.contacts[high].phone) {
      
      comparisons++;
      
      if (low === high) {
        if (this.contacts[low].phone === searchPhone) {
          console.log(`✅ Found contact with phone "${searchPhone}"`);
          return this.contacts[low];
        }
        break;
      }
      
      // Estimate position using interpolation formula
      // For phone numbers, we'll use a simple linear interpolation
      const pos = low + Math.floor(
        ((parseFloat(searchPhone) - parseFloat(this.contacts[low].phone)) / 
         (parseFloat(this.contacts[high].phone) - parseFloat(this.contacts[low].phone))) * 
        (high - low)
      );
      
      const safePos = Math.max(low, Math.min(high, pos));
      
      console.log(`  Interpolated position: ${safePos + 1} (${this.contacts[safePos].phone})`);
      
      if (this.contacts[safePos].phone === searchPhone) {
        const endTime = Date.now();
        console.log(`✅ Found phone "${searchPhone}" at position ${safePos + 1} after ${comparisons} comparisons`);
        
        this.searchHistory.push({
          method: 'Interpolation Search',
          query: searchPhone,
          found: true,
          comparisons,
          timeMs: endTime - startTime
        });
        
        return this.contacts[safePos];
      }
      
      if (this.contacts[safePos].phone < searchPhone) {
        low = safePos + 1;
      } else {
        high = safePos - 1;
      }
    }
    
    const endTime = Date.now();
    console.log(`❌ Phone "${searchPhone}" not found after ${comparisons} comparisons`);
    
    this.searchHistory.push({
      method: 'Interpolation Search',
      query: searchPhone,
      found: false,
      comparisons,
      timeMs: endTime - startTime
    });
    
    return null;
  }

  /**
   * Fuzzy Search: Find contacts with similar names (typo tolerance)
   * Uses Levenshtein distance for similarity
   */
  fuzzySearchByName(searchName, maxDistance = 2) {
    console.log(`\n🔍 Fuzzy Search for "${searchName}" (max distance: ${maxDistance}):`);
    
    const matches = [];
    let comparisons = 0;
    const startTime = Date.now();
    
    for (const contact of this.contacts) {
      comparisons++;
      const distance = this.levenshteinDistance(
        contact.name.toLowerCase(), 
        searchName.toLowerCase()
      );
      
      if (distance <= maxDistance) {
        matches.push({ contact, distance });
        console.log(`  Found similar: "${contact.name}" (distance: ${distance})`);
      }
    }
    
    // Sort by similarity (distance)
    matches.sort((a, b) => a.distance - b.distance);
    
    const endTime = Date.now();
    console.log(`✅ Found ${matches.length} similar matches after ${comparisons} comparisons (${endTime - startTime}ms)`);
    
    this.searchHistory.push({
      method: 'Fuzzy Search',
      query: searchName,
      found: matches.length > 0,
      comparisons,
      timeMs: endTime - startTime,
      matchCount: matches.length
    });
    
    return matches.map(match => match.contact);
  }

  /**
   * Multi-field Search: Search across name, phone, and email
   */
  multiFieldSearch(query) {
    console.log(`\n🔎 Multi-field Search for "${query}":`);
    
    const matches = [];
    let comparisons = 0;
    const startTime = Date.now();
    
    for (const contact of this.contacts) {
      comparisons++;
      
      const searchIn = [
        contact.name.toLowerCase(),
        contact.phone,
        contact.email.toLowerCase()
      ];
      
      const found = searchIn.some(field => 
        field.includes(query.toLowerCase())
      );
      
      if (found) {
        matches.push(contact);
        console.log(`  Match: ${contact.name} (found in multiple fields)`);
      }
    }
    
    const endTime = Date.now();
    console.log(`✅ Found ${matches.length} matches across all fields (${endTime - startTime}ms)`);
    
    this.searchHistory.push({
      method: 'Multi-field Search',
      query,
      found: matches.length > 0,
      comparisons,
      timeMs: endTime - startTime
    });
    
    return matches;
  }

  /**
   * Category Search: Find all contacts in a specific category
   */
  searchByCategory(category) {
    console.log(`\n📁 Category Search for "${category}":`);
    
    const matches = this.contacts.filter(contact => 
      contact.category.toLowerCase() === category.toLowerCase()
    );
    
    console.log(`Found ${matches.length} contacts in "${category}" category:`);
    matches.forEach(contact => {
      console.log(`  - ${contact.toString()}`);
    });
    
    return matches;
  }

  /**
   * Search Recent Contacts: Find recently called contacts
   */
  searchRecentContacts(days = 7) {
    console.log(`\n🕒 Recent Contacts Search (last ${days} days):`);
    
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - days);
    
    const recentContacts = this.contacts
      .filter(contact => contact.lastCalled && contact.lastCalled >= cutoffDate)
      .sort((a, b) => b.lastCalled - a.lastCalled); // Most recent first
    
    console.log(`Found ${recentContacts.length} recently called contacts:`);
    recentContacts.forEach(contact => {
      const daysSince = Math.floor((Date.now() - contact.lastCalled) / (1000 * 60 * 60 * 24));
      console.log(`  - ${contact.name} (${daysSince} days ago, ${contact.callCount} calls)`);
    });
    
    return recentContacts;
  }

  /**
   * Helper method: Calculate Levenshtein distance for fuzzy search
   */
  levenshteinDistance(str1, str2) {
    const matrix = [];
    
    for (let i = 0; i <= str2.length; i++) {
      matrix[i] = [i];
    }
    
    for (let j = 0; j <= str1.length; j++) {
      matrix[0][j] = j;
    }
    
    for (let i = 1; i <= str2.length; i++) {
      for (let j = 1; j <= str1.length; j++) {
        if (str2.charAt(i - 1) === str1.charAt(j - 1)) {
          matrix[i][j] = matrix[i - 1][j - 1];
        } else {
          matrix[i][j] = Math.min(
            matrix[i - 1][j - 1] + 1, // substitution
            matrix[i][j - 1] + 1,     // insertion
            matrix[i - 1][j] + 1      // deletion
          );
        }
      }
    }
    
    return matrix[str2.length][str1.length];
  }

  /**
   * Helper method: Binary search within a range
   */
  binarySearchInRange(searchName, left, right) {
    while (left <= right) {
      const mid = Math.floor((left + right) / 2);
      const comparison = this.contacts[mid].name.toLowerCase().localeCompare(searchName.toLowerCase());
      
      if (comparison === 0) {
        return this.contacts[mid];
      } else if (comparison > 0) {
        right = mid - 1;
      } else {
        left = mid + 1;
      }
    }
    return null;
  }

  /**
   * Sort contacts by name (required for binary search)
   */
  sortContactsByName() {
    console.log('  Sorting contacts by name...');
    this.contacts.sort((a, b) => a.name.toLowerCase().localeCompare(b.name.toLowerCase()));
    this.isSorted = true;
    this.sortedBy = 'name';
  }

  /**
   * Sort contacts by phone (required for interpolation search)
   */
  sortContactsByPhone() {
    console.log('  Sorting contacts by phone number...');
    this.contacts.sort((a, b) => a.phone.localeCompare(b.phone));
    this.isSorted = true;
    this.sortedBy = 'phone';
  }

  /**
   * Display all contacts
   */
  displayContacts() {
    console.log(`\n📞 ${this.ownerName} Contact Book (${this.contacts.length} contacts):`);
    console.log('----------------------------------------------------');
    
    if (this.contacts.length === 0) {
      console.log('No contacts found');
      return;
    }
    
    this.contacts.forEach((contact, index) => {
      console.log(`${(index + 1).toString().padStart(2)}. ${contact.toString()}`);
    });
  }

  /**
   * Display search performance history
   */
  displaySearchHistory() {
    console.log('\n📈 Search Performance History:');
    console.log('Method\t\t\tQuery\t\tFound\tComparisons\tTime (ms)');
    console.log('------------------------------------------------------------------------');
    
    this.searchHistory.forEach(search => {
      const found = search.found ? '✅' : '❌';
      console.log(`${search.method.padEnd(20)}\t${search.query.padEnd(12)}\t${found}\t${search.comparisons}\t\t${search.timeMs}`);
    });
    
    if (this.searchHistory.length > 0) {
      const avgTime = this.searchHistory.reduce((sum, s) => sum + s.timeMs, 0) / this.searchHistory.length;
      const avgComparisons = this.searchHistory.reduce((sum, s) => sum + s.comparisons, 0) / this.searchHistory.length;
      console.log(`\nAverages: ${avgComparisons.toFixed(1)} comparisons, ${avgTime.toFixed(1)}ms`);
    }
  }

  /**
   * Real-world applications demonstration
   */
  static demonstrateApplications() {
    console.log(`\n🌟 Real-World Applications of Searching:\n\n` +
      `1. 🔍 Web Search Engines: Finding web pages\n` +
      `2. 📊 Database Queries: Retrieving specific records\n` +
      `3. 🎮 Game AI: Pathfinding and decision trees\n` +
      `4. 📦 E-commerce: Product search and filtering\n` +
      `5. 🌐 DNS Lookups: Finding server addresses\n` +
      `6. 📁 File Systems: Locating files and folders\n` +
      `7. 🧬 Bioinformatics: DNA sequence matching\n`);
  }
}

/**
 * Hash Table for O(1) Contact Lookup
 */
class ContactHashTable {
  constructor(size = 50) {
    this.size = size;
    this.table = new Array(size);
    for (let i = 0; i < size; i++) {
      this.table[i] = [];
    }
    this.count = 0;
  }

  /**
   * Simple hash function
   */
  hash(key) {
    let hash = 0;
    for (let i = 0; i < key.length; i++) {
      hash += key.charCodeAt(i);
    }
    return hash % this.size;
  }

  /**
   * Insert contact
   * Average Time Complexity: O(1)
   */
  insert(contact) {
    const index = this.hash(contact.name.toLowerCase());
    const bucket = this.table[index];
    
    // Check if contact already exists
    const existingIndex = bucket.findIndex(c => c.name === contact.name);
    if (existingIndex !== -1) {
      bucket[existingIndex] = contact; // Update
    } else {
      bucket.push(contact); // Insert new
      this.count++;
    }
    
    console.log(`➕ Added "${contact.name}" to hash table (bucket ${index})`);
  }

  /**
   * Search for contact
   * Average Time Complexity: O(1)
   */
  search(name) {
    console.log(`\n#️⃣  Hash Table Search for "${name}":`);
    
    const index = this.hash(name.toLowerCase());
    const bucket = this.table[index];
    
    console.log(`  Calculated hash: ${index}`);
    console.log(`  Bucket size: ${bucket.length}`);
    
    for (const contact of bucket) {
      if (contact.name.toLowerCase() === name.toLowerCase()) {
        console.log(`✅ Found "${name}" in hash table`);
        return contact;
      }
    }
    
    console.log(`❌ "${name}" not found in hash table`);
    return null;
  }

  /**
   * Display hash table statistics
   */
  displayStats() {
    console.log('\n📊 Hash Table Statistics:');
    
    let maxBucketSize = 0;
    let emptyBuckets = 0;
    
    for (let i = 0; i < this.size; i++) {
      const bucketSize = this.table[i].length;
      if (bucketSize === 0) {
        emptyBuckets++;
      }
      maxBucketSize = Math.max(maxBucketSize, bucketSize);
    }
    
    const loadFactor = this.count / this.size;
    
    console.log(`Total contacts: ${this.count}`);
    console.log(`Table size: ${this.size}`);
    console.log(`Load factor: ${loadFactor.toFixed(2)}`);
    console.log(`Empty buckets: ${emptyBuckets}`);
    console.log(`Max bucket size: ${maxBucketSize}`);
  }
}

/**
 * Searching Practice Problems
 */
class SearchingPracticeProblems {
  /**
   * Problem 1: Find first and last occurrence
   */
  static findFirstAndLastOccurrence(contacts, name) {
    console.log(`\n🔍 Finding first and last occurrence of "${name}":`);
    
    // Sort contacts first
    contacts.sort((a, b) => a.name.toLowerCase().localeCompare(b.name.toLowerCase()));
    
    const findFirst = () => {
      let left = 0, right = contacts.length - 1, result = -1;
      
      while (left <= right) {
        const mid = Math.floor((left + right) / 2);
        if (contacts[mid].name.toLowerCase() === name.toLowerCase()) {
          result = mid;
          right = mid - 1; // Continue searching left
        } else if (contacts[mid].name.toLowerCase() < name.toLowerCase()) {
          left = mid + 1;
        } else {
          right = mid - 1;
        }
      }
      return result;
    };
    
    const findLast = () => {
      let left = 0, right = contacts.length - 1, result = -1;
      
      while (left <= right) {
        const mid = Math.floor((left + right) / 2);
        if (contacts[mid].name.toLowerCase() === name.toLowerCase()) {
          result = mid;
          left = mid + 1; // Continue searching right
        } else if (contacts[mid].name.toLowerCase() < name.toLowerCase()) {
          left = mid + 1;
        } else {
          right = mid - 1;
        }
      }
      return result;
    };
    
    const first = findFirst();
    const last = findLast();
    
    if (first === -1) {
      console.log(`  "${name}" not found`);
    } else {
      console.log(`  First occurrence: position ${first + 1}`);
      console.log(`  Last occurrence: position ${last + 1}`);
      console.log(`  Total occurrences: ${last - first + 1}`);
    }
    
    return { first, last };
  }

  /**
   * Problem 2: Find peak element (contact with max calls)
   */
  static findPeakContact(contacts) {
    console.log('\n🏀 Finding peak contact (most calls):');
    
    if (contacts.length === 0) return null;
    if (contacts.length === 1) return contacts[0];
    
    let left = 0, right = contacts.length - 1;
    
    while (left < right) {
      const mid = Math.floor((left + right) / 2);
      
      if (contacts[mid].callCount > contacts[mid + 1].callCount) {
        right = mid;
      } else {
        left = mid + 1;
      }
    }
    
    console.log(`  Peak contact: ${contacts[left].name} (${contacts[left].callCount} calls)`);
    return contacts[left];
  }

  /**
   * Problem 3: Search in rotated sorted array
   */
  static searchInRotatedContacts(contacts, targetName) {
    console.log(`\n🔄 Searching in rotated contact list for "${targetName}":`);
    
    let left = 0, right = contacts.length - 1;
    
    while (left <= right) {
      const mid = Math.floor((left + right) / 2);
      
      if (contacts[mid].name.toLowerCase() === targetName.toLowerCase()) {
        console.log(`  Found "${targetName}" at position ${mid + 1}`);
        return mid;
      }
      
      // Check which half is sorted
      if (contacts[left].name.toLowerCase() <= contacts[mid].name.toLowerCase()) {
        // Left half is sorted
        if (targetName.toLowerCase() >= contacts[left].name.toLowerCase() && 
            targetName.toLowerCase() < contacts[mid].name.toLowerCase()) {
          right = mid - 1;
        } else {
          left = mid + 1;
        }
      } else {
        // Right half is sorted
        if (targetName.toLowerCase() > contacts[mid].name.toLowerCase() && 
            targetName.toLowerCase() <= contacts[right].name.toLowerCase()) {
          left = mid + 1;
        } else {
          right = mid - 1;
        }
      }
    }
    
    console.log(`  "${targetName}" not found in rotated list`);
    return -1;
  }

  /**
   * Problem 4: Find K closest contacts to a given name (alphabetically)
   */
  static findKClosestContacts(contacts, targetName, k) {
    console.log(`\n🎯 Finding ${k} closest contacts to "${targetName}":`);
    
    // Sort contacts
    contacts.sort((a, b) => a.name.toLowerCase().localeCompare(b.name.toLowerCase()));
    
    // Find the position where targetName would be inserted
    let left = 0, right = contacts.length - 1, insertPos = contacts.length;
    
    while (left <= right) {
      const mid = Math.floor((left + right) / 2);
      if (contacts[mid].name.toLowerCase() >= targetName.toLowerCase()) {
        insertPos = mid;
        right = mid - 1;
      } else {
        left = mid + 1;
      }
    }
    
    // Find k closest elements
    left = insertPos - 1;
    right = insertPos;
    const result = [];
    
    while (result.length < k && (left >= 0 || right < contacts.length)) {
      if (left < 0) {
        result.push(contacts[right++]);
      } else if (right >= contacts.length) {
        result.push(contacts[left--]);
      } else {
        // Compare distances
        const leftDist = Math.abs(contacts[left].name.toLowerCase().localeCompare(targetName.toLowerCase()));
        const rightDist = Math.abs(contacts[right].name.toLowerCase().localeCompare(targetName.toLowerCase()));
        
        if (leftDist <= rightDist) {
          result.push(contacts[left--]);
        } else {
          result.push(contacts[right++]);
        }
      }
    }
    
    console.log(`  Closest contacts:`);
    result.forEach((contact, index) => {
      console.log(`    ${index + 1}. ${contact.name}`);
    });
    
    return result;
  }
}

// Export for use in other modules
export { 
  Contact, 
  PhoneContactBook, 
  ContactHashTable, 
  SearchingPracticeProblems 
};

import { fileURLToPath } from 'url';
import { argv } from 'process';
const __filename = fileURLToPath(import.meta.url);

// Example usage and demonstration
if (argv[1] === __filename) {
  console.log('📞 Welcome to the Phone Contact Book Searching Module!\n');
  
  // Create contact book
  const myPhone = new PhoneContactBook('John\'s iPhone');
  
  // Add contacts
  console.log('📞 Adding contacts to phone book:');
  myPhone.addContact('Alice Johnson', '555-0101', 'alice@email.com', 'work', true);
  myPhone.addContact('Bob Smith', '555-0102', 'bob@email.com', 'personal');
  myPhone.addContact('Charlie Brown', '555-0103', 'charlie@email.com', 'family');
  myPhone.addContact('Diana Prince', '555-0104', 'diana@email.com', 'work');
  myPhone.addContact('Eve Adams', '555-0105', 'eve@email.com', 'personal');
  myPhone.addContact('Frank Wilson', '555-0106', 'frank@email.com', 'work');
  myPhone.addContact('Grace Lee', '555-0107', 'grace@email.com', 'family');
  myPhone.addContact('Henry Davis', '555-0108', 'henry@email.com', 'personal');
  myPhone.addContact('Ivy Chen', '555-0109', 'ivy@email.com', 'work');
  myPhone.addContact('Jack Taylor', '555-0110', 'jack@email.com', 'personal');
  
  // Simulate some call activity
  myPhone.contacts[0].call(); // Alice
  myPhone.contacts[2].call(); // Charlie
  myPhone.contacts[4].call(); // Eve
  myPhone.contacts[0].call(); // Alice again
  
  myPhone.displayContacts();
  
  // Demonstrate different search algorithms
  console.log('\n🔍 Search Algorithm Demonstrations:');
  
  // 1. Linear Search
  myPhone.linearSearchByName('Diana Prince');
  myPhone.linearSearchByName('NonExistent Person');
  
  // 2. Binary Search
  myPhone.binarySearchByName('Charlie Brown');
  myPhone.binarySearchByName('Zoe Miller');
  
  // 3. Jump Search
  myPhone.jumpSearchByName('Grace Lee');
  
  // 4. Exponential Search
  myPhone.exponentialSearchByName('Ivy Chen');
  
  // 5. Interpolation Search (by phone)
  myPhone.interpolationSearchByPhone('555-0105');
  
  // 6. Fuzzy Search
  myPhone.fuzzySearchByName('Alise Johnson'); // Typo in Alice
  myPhone.fuzzySearchByName('Bob Smyth'); // Typo in Smith
  
  // 7. Multi-field Search
  myPhone.multiFieldSearch('555-0104');
  myPhone.multiFieldSearch('work');
  
  // 8. Category Search
  myPhone.searchByCategory('work');
  myPhone.searchByCategory('family');
  
  // 9. Recent Contacts
  myPhone.searchRecentContacts(30);
  
  // Display search performance comparison
  myPhone.displaySearchHistory();
  
  // Demonstrate Hash Table
  console.log('\n#️⃣  Hash Table Demonstration:');
  const hashTable = new ContactHashTable(10);
  
  // Add contacts to hash table
  myPhone.contacts.forEach(contact => {
    hashTable.insert(contact);
  });
  
  hashTable.displayStats();
  
  // Search in hash table
  hashTable.search('Alice Johnson');
  hashTable.search('NonExistent Person');
  
  // Show real-world applications
  PhoneContactBook.demonstrateApplications();
  
  // Practice problems
  console.log('\n🧠 Searching Practice Problems:');
  
  console.log('\n1. Find First and Last Occurrence:');
  // Add duplicate names for testing
  myPhone.addContact('Alice Johnson', '555-0201', 'alice2@email.com', 'personal');
  SearchingPracticeProblems.findFirstAndLastOccurrence(myPhone.contacts, 'Alice Johnson');
  
  console.log('\n2. Find Peak Contact:');
  SearchingPracticeProblems.findPeakContact(myPhone.contacts);
  
  console.log('\n3. K Closest Contacts:');
  SearchingPracticeProblems.findKClosestContacts(myPhone.contacts, 'David Miller', 3);
  
  console.log('\n✅ Search algorithm demonstrations complete!');
}