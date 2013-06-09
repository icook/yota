class InvalidContextException(Exception):
        pass


class NotCallableException(Exception):
        pass


class ValidationError(Exception):
        pass


class DataAccessException(Exception):
    def __str__(self):
        return ("Attempted to validate data that was not passed in to the "
               "validation method. Check to ensure validation is happening"
               " on form submission")
