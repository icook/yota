import platform
import re
import urllib
import urllib2
import urlparse
from yota.exceptions import ValidationError, FormDataAccessException

class ValidatorBase(object):
    """ The base validation class """
    pass


class MinLengthValidator(ValidatorBase):
    __slots__=["message", "min_length"]
    def __init__(self, length, message=None):
        self.min_length = length
        self.message = message if message else "Minimum allowed length {}".format(length)
        super(MinLengthValidator, self).__init__()

    def __call__(self, value):
        if len(value) < self.min_length:
            return {'message': self.message}


class MaxLengthValidator(ValidatorBase):
    __slots__=["message", "max_length"]
    def __init__(self, length, message=None):
        self.max_length = length
        self.message = message if message else "Maximum allowed length {}".format(length)
        super(MinLengthValidator, self).__init__()

    def __call__(self, value):
        if len(value) > self.min_length:
            return {'message': self.message}

class RequiredValidator(ValidatorBase):
    __slots__=["message"]
    def __init__(self, message=None):
        self.message = message if message else "A value is required"
        super(RequiredValidator, self).__init__()

    def __call__(self, value):
        if len(value) == 0:
            return {'message': self.message}


class EmailValidator(ValidatorBase):
    user_regex = re.compile(
        r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*$"  # dot-atom
        r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-\011\013\014\016-\177])*"$)', # quoted-string
        re.IGNORECASE)
    domain_regex = re.compile(
        r'(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?$)'  # domain
        # literal form, ipv4 address (SMTP 4.1.3)
        r'|^\[(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}\]$',
        re.IGNORECASE)
    domain_whitelist = ['localhost']
    def __init__(self, length, message=None):
        self.regex = regex
        self.message = message if message else "Maximum allowed length {}".format(length)
        super(MinLengthValidator, self).__init__()

    def __call__(self, value):
        if not value or '@' not in value:
            return {'message': self.message}

        user_part, domain_part = value.rsplit('@', 1)

        if not self.user_regex.match(user_part):
            return {'message': self.message}

        if (not domain_part in self.domain_whitelist and
                not self.domain_regex.match(domain_part)):
            # Try for possible IDN domain-part
            try:
                domain_part = domain_part.encode('idna').decode('ascii')
                if not self.domain_regex.match(domain_part):
                    return {'message': self.message}
                else:
                    return
            except UnicodeError:
                pass

        return {'message': self.message}

class Check(object):

    def __init__(self, validator, target, args=None, kwargs=None):
        self.validator = validator
        self.target = target
        if not args:
            self.args = []
        if not kwargs:
            self.kwargs = {}
        self._attr_name = None

    def resolve_attr_names(self, data, form):
        # Load up the args and kwargs that were passed with submission
        # data in order to pass into the validator. Called from
        # validate function.
        print id(self.args)
        for i in enumerate(self.args):
            node = form.get_by_attr(self.args[i])
            try:
                self.args[i] = data[node.name]
            except KeyError:
                raise FormDataAccessException
        for val, i in self.kwargs.iteritems():
            node = form.get_by_attr(val)
            try:
                self.kwargs[i] = data[node.name]
            except KeyError:
                raise FormDataAccessException
        if len(self.args) == 0 and len(self.kwargs) == 0:
            node = form.get_by_attr(self.target)
            try:
                self.args.append(data[node.name])
            except KeyError:
                raise FormDataAccessException
        self.target = form.get_by_attr(self.target)
    def __str__(self):
        return "Check<validator: {}, target: {}, args: {}, kwargs: {}>".format(self.validator, self.target, self.args, self.kwargs)

    def validate(self):
        # Convenience function making Form validate semantics cleaner
        return self.validator(*self.args, **self.kwargs)
