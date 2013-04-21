import platform
from collections import namedtuple
import re
import urllib
import urllib2
import urlparse
from yota.exceptions import ValidationError, FormDataAccessException

class ValidatorBase(object):
    """
    Validators in Yota are a fairly abstract concept. Essentially they are
    callables that get executed by one of the three different validation methods
    exposed by the `Form` class. Validators are supplied with a NamedTuple for
    each attribute name that is passed to their parent `Check` object in `Form`
    definition. The named tuple has two attributes: node and data. Node will be
    a reference to the actual `Node` instance that is linked to the specified
    attribute name while data is populated with the submission data associated
    with that `Node`. This allows you to write a validator that accepts an
    arbitrarily large amount of data with which to generate an output.

    Return Expectations
    ====================

    Validators are expected to return either a single tuple or a list of tuples,
    or None indicating no validation message to be transferred. The tuples must
    contain the a target node as their first parameter and a dictionary of
    validation results as the second parameter. There are a couple special
    attributes that can be defined in this dictionary, but these will be
    discussed a little later. How this data is used varies slightly depending on
    the validation method used.

    Validator Semantics
    =====================

    With the regular form validation method `Form.validate_render` the data will
    get passed directly to the `Node` rendering context when the form is
    re-rendered as the ``error`` attribute. In your `Node` template, the error
    can then be used for anything related to rendering and will contain
    everything in the dictionary.

    With either the piecewise json validation method or the regular json
    validation method the data data will get translated into a JSON object that
    is packed into antoher object where the key is the `Node.id` of your target
    `Node` passed back as the validation result.

    Special Key Values
    =====================

    At the moment they only special key is 'block'. If set to False the
    validation message will not prevent the form from submitting. This is useful
    for things like notification of password strength, etc.
    """
    pass


class MinLengthValidator(ValidatorBase):
    """ Checks to see if data is at least :length long.

    :param length: The minimum length of the data.
    :type length: integer

    :param message: The message to present to the user upon failure.
    :type message: string
    """
    __slots__=["message", "min_length"]
    def __init__(self, length, message=None):
        self.min_length = length
        self.message = message if message else "Minimum allowed length {}".format(length)
        super(MinLengthValidator, self).__init__()

    def __call__(self, target):
        if len(target.data) < self.min_length:
            return (target.node, {'message': self.message})


class MaxLengthValidator(ValidatorBase):
    """ Checks to see if data is at most :length long.

    :param length: The maximum length of the data.
    :type length: integer

    :param message: The message to present to the user upon failure.
    :type message: string
    """
    __slots__=["message", "max_length"]
    def __init__(self, length, message=None):
        self.max_length = length
        self.message = message if message else "Maximum allowed length {}".format(length)
        super(MinLengthValidator, self).__init__()

    def __call__(self, target):
        if len(target.data) > self.min_length:
            return (target.node, {'message': self.message})

class RequiredValidator(ValidatorBase):
    """ Checks to make sure the user entered something.

    :param message: (optional) The message to present to the user upon failure.
    :type message: string
    """
    __slots__=["message"]
    def __init__(self, message=None):
        self.message = message if message else "A value is required"
        super(RequiredValidator, self).__init__()

    def __call__(self, target):
        if len(target.data) == 0:
            return (target.node, {'message': self.message})


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

    def __call__(self, target):
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

        return (value.node, {'message': self.message})

class Check(object):
    """ This object wraps a validator callable and is intended to be used in
    your `Form` subclass definition.

    :param callable validator: This is required to be a callable object that
    will carry out the actual validation. Many generic validators exist or you
    can roll your own.

    :param list args: A list of strings, or a single string, representing that
    _attr_name of the `Node` you would like passed into the validator. Once a
    validator is called this string will get resolved into a NamedTuple that
    will be passed into the validator callable.

    :param dict kwargs: Same as args above except it allows passing in node
    information as keyword arguments to the validator callable.

    `Check` objects are desinged to be declared in your form subclass in one of
    two ways. Explicit:::

        class MyForm(yota.Form):
            # This syntax shortens up the above explicit syntax for simple
            # validators
            first = EntryNode(title='First name')
            _first_valid = Check(MinLengthValidator(5), 'first')

    The syntax above binds our `MinLengthValidator` to a Node with attribute
    name 'first'. How it matches up your string 'first' to the correct `Node`
    instance is a bit of magic behind the scenes, but just know that it matches
    up to the attribute name you give the node in the your `Form` class
    definition. If you later add a `Node` dynamically it will need to specify
    the _attr_name upon declaration explicity. More on this in Dynamically
    Adding Nodes.

    Implicit declaration is a nice option for simple validators, and is simply
    syntactic sugar for the above syntax:::

        class MyForm(yota.Form):
            # This syntax shortens up the above explicit syntax for simple
            # validators. An args of 'first' will automatically be added to the
            # Check object for you.
            first = EntryNode(title='First name',
                              validator=Check(MinLengthValidator(5)))

            # This even more brief syntax will automatically built the Check
            # object for you
            last = EntryNode(title='Last name', validator=MinLengthValidator(5)

            # This syntax however is just like above. Be aware that your
            # attribute name will not be automatically added since your
            # explicitly defining args
            address = EntryNode(validator=
                        Check(MinLengthValidator(9), 'address'))

    If neither kwargs or args are specified and cannot be implicitly determined
    an exception will be thrown. """

    def __init__(self, validator, *args, **kwargs):
        self.validator = validator
        if not args:
            self.args = []
        else:
            self.args = list(args)

        if not kwargs:
            self.kwargs = {}
        else:
            self.kwargs = kwargs

        self._attr_name = None
        self.resolved = False

    def resolve_attr_names(self, data, form):
        """ Called internally by the validation methods this resolves all arg
        and kawrg strings to their respective `Node` objects and replaces them
        with a KeyedTuple containing the submitted data and the Node object
        reference. """

        if self.resolved:
            return


        NodeData = namedtuple('NodeData', ['node', 'data'])

        # Process args
        for key, arg in enumerate(self.args):
            node = form.get_by_attr(arg)
            try:
                self.args[key] = NodeData(node, data[node.name])
            except KeyError:
                raise FormDataAccessException

        # Process kwargs
        for val, i in self.kwargs.iteritems():
            node = form.get_by_attr(val)
            try:
                self.kwargs[i] = NodeData(node, data[node.name])
            except KeyError:
                raise FormDataAccessException

        self.resolved = True

    def __str__(self):
        return "Check<validator: {}, args: {}, kwargs: {}>".format(self.validator, self.args, self.kwargs)

    def validate(self):
        # Convenience function making Form validate semantics cleaner
        return self.validator(*self.args, **self.kwargs)
