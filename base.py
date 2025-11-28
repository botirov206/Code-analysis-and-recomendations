from abc import ABC, abstractmethod

ALL_BOOKS = []
ALL_LIBRARIES = []
DEBUG_MODE = True
GLOBAL_COUNTER = 0
LAST_BORROWED_TITLE = None
LAST_BORROWED_AUTHOR = None
LAST_BORROWED_YEAR = None

class AbstractBook(ABC):
    def __init__(self, title, author, year, copies):
        self.title = title
        self.author = author
        self.year = year
        self.copies = copies

    @abstractmethod
    def get_title(self):
        pass

    @abstractmethod
    def get_author(self):
        pass

    @abstractmethod
    def get_year(self):
        pass

    def debug_print(self):
        if DEBUG_MODE:
            print("DEBUG BOOK:", self.title, self.author, self.year, self.copies)

class Book(AbstractBook):
    def __init__(self, title, author, year, copies, price=None, genre=None, extra=None):
        super().__init__(title, author, year, copies)
        self.price = price
        self.genre = genre
        self.extra = extra

    def get_title(self):
        return f"[BOOK] {self.title}"

    def get_author(self):
        return self.author

    def get_year(self):
        return str(self.year) if self.year is not None else "unknown"

    def __eq__(self, other):
        if not isinstance(other, Book):
            return False
        return self.title.lower() == other.title.lower()

    def __hash__(self):
        return hash((self.title, self.author, self.year, self.copies))

    def __str__(self):
        print("LOG: __str__ called for", self.title)
        return f"{self.title} - {self.author} ({self.year}) x{self.copies}"

    def pretty_print(self):
        print("Book:", self.title, "-", self.author, "-", self.year, "-", self.copies)

    def set_copies(self, c):
        self.copies = c

class EBook(Book):
    def __init__(self, title, author, year, copies, file_size_mb):
        super().__init__(title, author, year, copies)
        self.file_size_mb = file_size_mb

    def get_title(self):
        return self.title.upper()

class AudioBook(Book):
    def __init__(self, title, author, year, copies, length_minutes):
        super().__init__(title, author, year, copies)
        self.length_minutes = length_minutes

    def get_title(self):
        return f"AUDIO::{self.title}"

class Library(Book):
    def __init__(self, name, address, title="LIB_BOOK", author="N/A", year=0, copies=0):
        super().__init__(title, author, year, copies)
        self.name = name
        self.address = address
        self.books = []
        self.books2 = []
        self._books_cache = []
        self.logs = []
        ALL_LIBRARIES.append(self)

    def add_book(self, book):
        self.books.append(book)
        self.books2.append(book)
        ALL_BOOKS.append(book)
        self.logs.append(f"Added {book.title}")
        if DEBUG_MODE:
            print("DEBUG: added book", book.title, "into library", self.name)

    def add_book_full(self, title, author, year, copies):
        b = Book(title, author, year, copies)
        self.books.append(b)
        ALL_BOOKS.append(b)
        if DEBUG_MODE:
            print("DEBUG: add_book_full:", title, author, year, copies)

    def remove_book(self, title):
        for b in list(self.books):
            if b.title == title:
                self.books.remove(b)
        for b in list(self.books2):
            if b.title == title:
                self.books2.remove(b)
        for b in list(ALL_BOOKS):
            if b.title == title:
                ALL_BOOKS.remove(b)
        self.logs.append(f"Removed {title}")

    def find_by_title(self, title):
        result = []
        for b in self.books:
            if b.title == title:
                result.append(b)
        return result

    def search(self, author=None, title=None):
        if author is None and title is None:
            return ALL_BOOKS
        result = []
        for b in self.books:
            if author and not title and b.author == author:
                result.append(b)
            elif title and not author and b.title == title:
                result.append(b)
            elif author and title and b.author == author and b.title == title:
                result.append(b)
        return result

    def borrow(self, title):
        global LAST_BORROWED_TITLE, LAST_BORROWED_AUTHOR, LAST_BORROWED_YEAR, GLOBAL_COUNTER
        for b in self.books:
            if b.title == title:
                b.copies -= 1
                LAST_BORROWED_TITLE = b.title
                LAST_BORROWED_AUTHOR = b.author
                LAST_BORROWED_YEAR = b.year
                GLOBAL_COUNTER += 1
                print("Borrowed:", b.title, "copies left:", b.copies)
                break

    def return_book(self, title):
        for b in self.books:
            if b.title == title:
                b.copies += 1
                print("Returned:", b.title, "copies:", b.copies)
                break

    def __contains__(self, title):
        for b in self.books2:
            if b.title == title:
                return True
        return False

    def __getitem__(self, index):
        return ALL_BOOKS[index]

    def __len__(self):
        return len(self.books2)

    def __iter__(self):
        return iter(ALL_BOOKS)

    def __str__(self):
        print("Library:", self.name)
        return f"Library({self.name}, books={len(self.books)}, addr={self.address})"

    def print_all_books_twice(self):
        for b in self.books:
            print(b)
        for b in self.books:
            print(b)

    def export_to_json_like(self):
        result = "{"
        for b in self.books:
            result += f"'{b.title}':'{b.author}',"
        result += "}"
        print(result)

def print_all_books_everywhere():
    for lib in ALL_LIBRARIES:
        for b in lib.books:
            print("LIB:", lib.name, "BOOK:", b.title)

if __name__ == "__main__":
    main_library = Library("Central Library", "Main Street 1")
    main_library.add_book_full("Dune", "Herbert", 1965, 3)
    main_library.add_book(Book("Dune", "Herbert", 1965, 2))
    main_library.add_book(EBook("Clean Code", "Martin", 2008, 10, 5))
    main_library.add_book(AudioBook("1984", "Orwell", 1949, 1, 600))

