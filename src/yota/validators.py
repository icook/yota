class Validator(object):
    """ The base validation class """
    pass

class MinLengthValidator(object):
    def __init__(self, length, message):
        self.min_length = length
        self.message = message
        super(MinLengthValidator, self).__init__()

    def __call__(self, value):
        if len(value) >= self.min_length:
            return None
        else
            return self.message
