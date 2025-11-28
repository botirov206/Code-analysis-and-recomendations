"""
Library Management System
A clean, efficient book library management application with proper OOP principles.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional


# ============================================================================
# BOOK CLASSES - Represent different types of books
# ============================================================================

class AbstractBook(ABC):
    """
    Abstract base class for all book types.
    Defines the common interface all books must implement.
    """
    
    def __init__(self, title: str, author: str, year: int, copies: int):
        """Initialize book with basic information."""
        self.title = title
        self.author = author
        self.year = year
        self.copies = copies

    @abstractmethod
    def get_display_name(self) -> str:
        """Return formatted display name for the book."""
        pass


class Book(AbstractBook):
    """Standard book with optional pricing and genre info."""
    
    def __init__(self, title: str, author: str, year: int, copies: int, 
                 price: Optional[float] = None, genre: Optional[str] = None):
        """Initialize a standard book."""
        super().__init__(title, author, year, copies)
        self.price = price
        self.genre = genre

    def get_display_name(self) -> str:
        """Return book title as display name."""
        return self.title

    def __eq__(self, other) -> bool:
        """Compare books by title (case-insensitive)."""
        if not isinstance(other, Book):
            return False
        return self.title.lower() == other.title.lower()

    def __hash__(self) -> int:
        """Hash using only immutable attributes (copies is mutable)."""
        return hash((self.title.lower(), self.author, self.year))

    def __str__(self) -> str:
        """Human-readable book representation."""
        return f"{self.title} - {self.author} ({self.year}) x{self.copies}"

    def __repr__(self) -> str:
        """Developer-friendly book representation."""
        return f"Book(title={self.title!r}, author={self.author!r}, year={self.year}, copies={self.copies})"

    def set_copies(self, count: int) -> None:
        """Update number of copies with validation."""
        if count < 0:
            raise ValueError("Copies cannot be negative")
        self.copies = count


class EBook(Book):
    """Electronic book with file size information."""
    
    def __init__(self, title: str, author: str, year: int, copies: int, file_size_mb: float):
        """Initialize an e-book."""
        super().__init__(title, author, year, copies)
        self.file_size_mb = file_size_mb

    def get_display_name(self) -> str:
        """Return formatted e-book display name."""
        return f"[EBOOK] {self.title.upper()}"


class AudioBook(Book):
    """Audio book with duration information."""
    
    def __init__(self, title: str, author: str, year: int, copies: int, length_minutes: int):
        """Initialize an audio book."""
        super().__init__(title, author, year, copies)
        self.length_minutes = length_minutes

    def get_display_name(self) -> str:
        """Return formatted audio book display name."""
        return f"[AUDIO] {self.title}"



# ============================================================================
# LIBRARY CLASS - Manages book collection
# ============================================================================

class Library:
    """
    Manages a collection of books with efficient O(1) lookups.
    Uses a dictionary for fast access by title instead of slow list searches.
    
    Features:
    - Add/remove books
    - Search by title, author, or both
    - Borrow/return books with validation
    - Track borrow history
    - Support standard Python operations (len, iteration, containment)
    """
    
    def __init__(self, name: str, address: str):
        """Initialize library with name and address."""
        self.name = name
        self.address = address
        self.books: Dict[str, Book] = {}          # key: lowercase title for case-insensitive lookup
        self.logs: List[str] = []                 # Activity log
        self._borrow_history: List[tuple] = []    # Track borrowed items

    # ========================================================================
    # BOOK MANAGEMENT - Add, remove, find books
    # ========================================================================

    def add_book(self, book: Book) -> None:
        """
        Add a book to the library.
        If book title exists, increases the copy count instead of adding duplicate.
        
        Args:
            book: Book object to add
        """
        key = book.title.lower()
        if key in self.books:
            # Merge with existing book (increase copies)
            self.books[key].copies += book.copies
        else:
            # Add new book
            self.books[key] = book
        self.logs.append(f"Added {book.title}")

    def add_book_full(self, title: str, author: str, year: int, copies: int) -> None:
        """
        Create a new book and add it to the library.
        Convenient method for direct book creation without pre-making Book object.
        
        Args:
            title: Book title
            author: Book author
            year: Publication year
            copies: Number of copies to add
        """
        book = Book(title, author, year, copies)
        self.add_book(book)

    def remove_book(self, title: str) -> bool:
        """
        Remove a book from the library by title.
        
        Args:
            title: Title of book to remove
            
        Returns:
            True if book was removed, False if not found
        """
        key = title.lower()
        if key in self.books:
            del self.books[key]
            self.logs.append(f"Removed {title}")
            return True
        return False

    def find_by_title(self, title: str) -> Optional[Book]:
        """
        Find a single book by title (case-insensitive).
        
        Args:
            title: Title to search for
            
        Returns:
            Book object if found, None otherwise
        """
        return self.books.get(title.lower())

    # ========================================================================
    # SEARCH - Query books by various criteria
    # ========================================================================

    def search(self, author: Optional[str] = None, title: Optional[str] = None) -> List[Book]:
        """
        Search books by author and/or title (case-insensitive).
        
        Args:
            author: Author name to filter by (optional)
            title: Book title to filter by (optional)
            
        Returns:
            List of matching books. Returns all books if both parameters are None.
            
        Examples:
            search()                              -> all books
            search(title="Dune")                  -> books with title "Dune"
            search(author="Frank Herbert")        -> books by Frank Herbert
            search(author="Orwell", title="1984") -> books by Orwell titled "1984"
        """
        # Return all books if no criteria specified
        if author is None and title is None:
            return list(self.books.values())
        
        # Filter by criteria
        result = []
        for book in self.books.values():
            matches_author = author is None or book.author.lower() == author.lower()
            matches_title = title is None or book.title.lower() == title.lower()
            if matches_author and matches_title:
                result.append(book)
        return result

    # ========================================================================
    # BORROWING - Check out and return books
    # ========================================================================

    def borrow(self, title: str) -> bool:
        """
        Borrow a book from the library.
        Decreases copy count and validates availability before borrowing.
        
        Args:
            title: Title of book to borrow
            
        Returns:
            True if successfully borrowed
            False if book not found or no copies available
        """
        book = self.find_by_title(title)
        if book is None or book.copies <= 0:
            return False
        
        book.copies -= 1
        self._borrow_history.append((book.title, book.author, book.year))
        print(f"Borrowed: {book.title}, copies left: {book.copies}")
        return True

    def return_book(self, title: str) -> bool:
        """
        Return a book to the library.
        Increases copy count.
        
        Args:
            title: Title of book to return
            
        Returns:
            True if successfully returned
            False if book not found
        """
        book = self.find_by_title(title)
        if book is None:
            return False
        book.copies += 1
        print(f"Returned: {book.title}, copies: {book.copies}")
        return True

    # ========================================================================
    # PYTHON MAGIC METHODS - Support standard operations
    # ========================================================================

    def __contains__(self, title: str) -> bool:
        """Check if a book exists in library (case-insensitive).
        
        Usage: 'Dune' in library
        """
        return title.lower() in self.books

    def __getitem__(self, index: int) -> Book:
        """Access book by index.
        
        Usage: book = library[0]
        """
        return list(self.books.values())[index]

    def __len__(self) -> int:
        """Get number of unique books in library.
        
        Usage: count = len(library)
        """
        return len(self.books)

    def __iter__(self):
        """Iterate over all books in library.
        
        Usage: for book in library: print(book)
        """
        return iter(self.books.values())

    def __str__(self) -> str:
        """User-friendly string representation."""
        return f"Library({self.name}, books={len(self.books)}, addr={self.address})"

    def __repr__(self) -> str:
        """Developer-friendly string representation."""
        return f"Library(name={self.name!r}, address={self.address!r}, books={len(self.books)})"

    # ========================================================================
    # GETTERS - Retrieve library information
    # ========================================================================

    def get_all_books(self) -> List[Book]:
        """Get list of all books in library."""
        return list(self.books.values())

    def get_borrow_history(self) -> List[tuple]:
        """
        Get history of all borrowed books.
        
        Returns:
            List of (title, author, year) tuples in order of borrowing
        """
        return self._borrow_history.copy()

    # ========================================================================
    # DISPLAY - Print library information
    # ========================================================================

    def print_info(self) -> None:
        """Print detailed library information to console."""
        print(f"Library: {self.name}")
        print(f"Address: {self.address}")
        print(f"Books: {len(self.books)}")
        print("=" * 50)
        for book in self.books.values():
            print(f"  {book}")
        print("=" * 50)



# ============================================================================
# MAIN - Example usage demonstrating all features
# ============================================================================

if __name__ == "__main__":
    # Create a library instance
    lib = Library("Central Library", "Main Street 1")
    
    # Add books using different methods
    print(">>> Adding books to library...\n")
    lib.add_book_full("Dune", "Frank Herbert", 1965, 3)
    lib.add_book(Book("1984", "George Orwell", 1949, 2))
    lib.add_book(EBook("Clean Code", "Robert Martin", 2008, 10, 5.2))
    lib.add_book(AudioBook("The Great Gatsby", "F. Scott Fitzgerald", 1925, 1, 480))
    
    # Display library information
    print("\n>>> Library Overview:")
    lib.print_info()
    
    # Test borrowing and returning
    print("\n>>> Testing Borrow/Return Operations:")
    lib.borrow("Dune")
    lib.borrow("1984")
    lib.return_book("Dune")
    
    # Test search functionality
    print("\n>>> Testing Search Functionality:")
    results = lib.search(author="Frank Herbert")
    print(f"Books by Frank Herbert: {[b.title for b in results]}")
    
    # Test containment checks
    print("\n>>> Testing Containment Checks:")
    print(f"'Dune' in library: {'Dune' in lib}")
    print(f"'Unknown Book' in library: {'Unknown Book' in lib}")
    
    # Display borrow history
    print("\n>>> Borrow History:")
    history = lib.get_borrow_history()
    if history:
        for title, author, year in history:
            print(f"  - {title} by {author} ({year})")
    else:
        print("  No borrow history yet")
