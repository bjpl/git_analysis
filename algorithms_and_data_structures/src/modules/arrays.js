/**
 * Arrays: Organizing Books on a Shelf
 * 
 * Just like organizing books on a shelf where each book has a specific position,
 * arrays store elements in consecutive memory locations with index-based access.
 */

class BookshelfArray {
  constructor(size = 10) {
    this.shelf = new Array(size).fill(null);
    this.capacity = size;
    this.currentBooks = 0;
  }

  /**
   * Add a book to a specific position on the shelf
   * Time Complexity: O(1) for direct placement, O(n) if shifting needed
   */
  addBook(position, book) {
    if (position < 0 || position >= this.capacity) {
      throw new Error('Position out of bounds - shelf doesn\'t have that spot!');
    }
    
    if (this.shelf[position] !== null) {
      console.log(`Moving books to make room for "${book}" at position ${position}`);
      // Shift books to the right to make space
      this.shiftBooksRight(position);
    }
    
    this.shelf[position] = book;
    this.currentBooks++;
    console.log(`📚 Placed "${book}" at position ${position}`);
  }

  /**
   * Find a book on the shelf (Linear Search)
   * Time Complexity: O(n)
   */
  findBook(title) {
    console.log(`🔍 Searching for "${title}" on the shelf...`);
    
    for (let i = 0; i < this.capacity; i++) {
      if (this.shelf[i] === title) {
        console.log(`✅ Found "${title}" at position ${i}`);
        return i;
      }
    }
    
    console.log(`❌ "${title}" not found on the shelf`);
    return -1;
  }

  /**
   * Remove a book from the shelf
   * Time Complexity: O(n) due to shifting
   */
  removeBook(position) {
    if (position < 0 || position >= this.capacity) {
      throw new Error('Position out of bounds!');
    }
    
    const removedBook = this.shelf[position];
    if (removedBook === null) {
      console.log('No book at that position to remove');
      return null;
    }
    
    // Shift books to the left to fill the gap
    this.shiftBooksLeft(position);
    this.currentBooks--;
    
    console.log(`📖 Removed "${removedBook}" from position ${position}`);
    return removedBook;
  }

  /**
   * Get book at specific position (Random Access)
   * Time Complexity: O(1)
   */
  getBookAt(position) {
    if (position < 0 || position >= this.capacity) {
      return null;
    }
    return this.shelf[position];
  }

  /**
   * Sort books alphabetically (like organizing by title)
   * Using Bubble Sort for educational purposes
   * Time Complexity: O(n²)
   */
  sortBooksByTitle() {
    console.log('📖 Organizing books alphabetically...');
    
    // Filter out null values for sorting
    const books = this.shelf.filter(book => book !== null);
    
    // Bubble sort
    for (let i = 0; i < books.length - 1; i++) {
      for (let j = 0; j < books.length - i - 1; j++) {
        if (books[j] > books[j + 1]) {
          // Swap books
          [books[j], books[j + 1]] = [books[j + 1], books[j]];
          console.log(`Swapped "${books[j + 1]}" with "${books[j]}"`);
        }
      }
    }
    
    // Clear shelf and place sorted books
    this.shelf.fill(null);
    books.forEach((book, index) => {
      this.shelf[index] = book;
    });
    
    console.log('✅ Books are now organized alphabetically!');
  }

  /**
   * Helper method to shift books right
   */
  shiftBooksRight(fromPosition) {
    for (let i = this.capacity - 1; i > fromPosition; i--) {
      this.shelf[i] = this.shelf[i - 1];
    }
  }

  /**
   * Helper method to shift books left
   */
  shiftBooksLeft(fromPosition) {
    for (let i = fromPosition; i < this.capacity - 1; i++) {
      this.shelf[i] = this.shelf[i + 1];
    }
    this.shelf[this.capacity - 1] = null;
  }

  /**
   * Display the current state of the bookshelf
   */
  displayShelf() {
    console.log('\n📚 Current Bookshelf:');
    console.log('Position: ', Array.from({length: this.capacity}, (_, i) => i.toString().padStart(2)).join(' | '));
    console.log('Book:     ', this.shelf.map(book => book ? book.slice(0, 10).padStart(10) : '   ---    ').join(' | '));
    console.log(`📊 ${this.currentBooks}/${this.capacity} books on shelf\n`);
  }

  /**
   * Real-world applications demonstration
   */
  static demonstrateApplications() {
    console.log(`
🌟 Real-World Applications of Arrays:

` +
      `1. 📱 Contact Lists: Phone contacts stored by index\n` +
      `2. 🎵 Music Playlists: Songs in ordered sequence\n` +
      `3. 📊 Spreadsheets: Rows and columns of data\n` +
      `4. 🖼️  Image Processing: Pixels in 2D arrays\n` +
      `5. 📈 Stock Prices: Historical data points\n` +
      `6. 🎮 Game Boards: Tic-tac-toe, Chess positions\n` +
      `7. 📚 Library Catalogs: Books organized by ID\n`);
  }
}

/**
 * Practice Problems for Arrays
 */
class ArrayPracticeProblems {
  /**
   * Problem 1: Find duplicate books on shelf
   */
  static findDuplicates(bookArray) {
    const seen = new Set();
    const duplicates = new Set();
    
    for (const book of bookArray) {
      if (seen.has(book)) {
        duplicates.add(book);
      } else {
        seen.add(book);
      }
    }
    
    return Array.from(duplicates);
  }

  /**
   * Problem 2: Rotate bookshelf (move books left or right)
   */
  static rotateShelf(books, positions) {
    const n = books.length;
    const rotated = new Array(n);
    
    for (let i = 0; i < n; i++) {
      const newPosition = (i + positions) % n;
      rotated[newPosition] = books[i];
    }
    
    return rotated;
  }

  /**
   * Problem 3: Find the most popular book genre
   */
  static findPopularGenre(books) {
    const genreCount = {};
    
    books.forEach(book => {
      if (book && book.genre) {
        genreCount[book.genre] = (genreCount[book.genre] || 0) + 1;
      }
    });
    
    let maxCount = 0;
    let popularGenre = null;
    
    for (const [genre, count] of Object.entries(genreCount)) {
      if (count > maxCount) {
        maxCount = count;
        popularGenre = genre;
      }
    }
    
    return { genre: popularGenre, count: maxCount };
  }
}

// Export for use in other modules
export { BookshelfArray, ArrayPracticeProblems };

// Example usage and demonstration
// Check if this is the main module being run
import { fileURLToPath } from 'url';
import { argv } from 'process';

const __filename = fileURLToPath(import.meta.url);

if (argv[1] === __filename) {
  console.log('🏠 Welcome to the Bookshelf Array Learning Module!\n');
  
  // Create a bookshelf
  const myShelf = new BookshelfArray(8);
  
  // Add some books
  console.log('📚 Adding books to the shelf:');
  myShelf.addBook(0, 'Harry Potter');
  myShelf.addBook(1, 'Lord of the Rings');
  myShelf.addBook(2, 'The Hobbit');
  myShelf.addBook(4, 'Dune');
  myShelf.addBook(6, '1984');
  
  myShelf.displayShelf();
  
  // Demonstrate search
  console.log('\n🔍 Searching for books:');
  myShelf.findBook('Dune');
  myShelf.findBook('Narnia');
  
  // Insert a book in the middle
  console.log('\n📖 Inserting a book in position 3:');
  myShelf.addBook(3, 'Foundation');
  myShelf.displayShelf();
  
  // Remove a book
  console.log('\n🗑️  Removing a book:');
  myShelf.removeBook(1);
  myShelf.displayShelf();
  
  // Sort books
  console.log('\n📊 Sorting books alphabetically:');
  myShelf.sortBooksByTitle();
  myShelf.displayShelf();
  
  // Show real-world applications
  BookshelfArray.demonstrateApplications();
  
  // Practice problems
  console.log('\n🧠 Practice Problems:');
  const bookList = ['Harry Potter', 'Dune', 'Harry Potter', '1984', 'Dune'];
  console.log('Duplicates found:', ArrayPracticeProblems.findDuplicates(bookList));
  
  const rotated = ArrayPracticeProblems.rotateShelf(['A', 'B', 'C', 'D'], 2);
  console.log('Rotated shelf:', rotated);
}