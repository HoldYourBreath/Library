class BookError(Exception):
    def __init__(self, message):
        self.msg = message


class BookNotFound(Exception):
    pass


class BasicBook:
    def __init__(self, **kwargs):
        self.isbn = None
        self.title = ''
        self.authors = []
        self.description = ''
        self.thumbnail = ''
        self.pages = 0
        self.publisher = ''
        self.format = ''
        self.publication_date = ''

        for parameter in vars(self):
            if parameter in kwargs:
                setattr(self, parameter, kwargs[parameter])

    def _get_params(self):
        return (self.isbn,
                self.title,
                self.pages,
                self.publisher,
                self.format,
                self.publication_date,
                self.description,
                self.thumbnail)


class BasicBookDescriptor(BasicBook):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.number_of_copies = 0
        if 'num_copies' in kwargs and kwargs['num_copies']:
            self.number_of_copies = kwargs['num_copies']
