class BookViewModel:
    def __init__(self, book):
        self.image = book['image']
        self.title = book['title']
        self.author = '、'.join(book['author'])
        self.publisher = book['publisher']
        self.pages = book['pages'] or ''
        self.price = book['price']
        self.isbn = book['isbn']
        self.summary = book['summary'] or ''
        self.pubdate = book['pubdate']
        self.binding = book['binding']

class BookCollection:
    def __init__(self):
        self.total = 0
        self.books = []
        self.keyword = ''

    def fill(self, yushuBook, keyword):
        self.total = yushuBook.total
        self.keyword = keyword
        self.books = [BookViewModel(book) for book in yushuBook.books]
