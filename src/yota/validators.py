import re
from yota.exceptions import NotCallableException


class MinLengthValidator(object):
    """ Checks to see if data is at least length long.

    :param length: The minimum length of the data.
    :type length: integer

    :param message: The message to present to the user upon failure.
    :type message: string
    """
    __slots__ = ["message", "min_length"]

    def __init__(self, length, message=None):
        self.min_length = length
        self.message = message if message else "Minimum allowed length {0}" \
            .format(length)
        super(MinLengthValidator, self).__init__()

    def __call__(self, target):
        if len(target.data) < self.min_length:
            target.add_error({'message': self.message})


class MaxLengthValidator(object):
    """ Checks to see if data is at most length long.

    :param length: The maximum length of the data.
    :type length: integer

    :param message: The message to present to the user upon failure.
    :type message: string
    """
    __slots__ = ["message", "max_length"]

    def __init__(self, length, message=None):
        self.max_length = length
        self.message = message if message else "Maximum allowed length {0}" \
            .format(length)
        super(MaxLengthValidator, self).__init__()

    def __call__(self, target):
        if len(target.data) > self.max_length:
            target.add_error({'message': self.message})


class NonBlockingDummyValidator(object):
    """ A dummy class for testing non-blocking validators
    """

    def __call__(self, target):
        target.add_error({'message': "I'm not blocking!", 'block': False})


class MatchingValidator(object):
    """ Checks if two nodes values match eachother. The error is delivered to
    the first node.

    :param message: (optional) The message to present to the user upon failure.
    :type message: string
    """
    __slots__ = ["message"]

    def __init__(self, message=None):
        self.message = message if message else "Fields must match"
        super(MatchingValidator, self).__init__()

    def __call__(self, target1, target2):
        if target1.data != target2.data:
            target1.add_error({'message': self.message})


class IntegerValidator(object):
    """ Checks if the value is an integer and converts it to one if it is

    :param message: (optional) The message to present to the user upon failure.
    :type message: string
    """
    __slots__ = ["message"]

    def __init__(self, message=None):
        self.message = message if message else "Value must only contain numbers"
        super(IntegerValidator, self).__init__()

    def __call__(self, target):
        try:
            target.data = int(target.data)
        except ValueError:
            target.add_error({'message': self.message})


class MinMaxValidator(object):
    """ Checks if the value is between the min and max values given

    :param message: (optional) The message to present to the user upon failure.
    :type message: string

    :param min: The minimum length of the data.
    :type length: integer

    :param max: The maximum length of the data.
    :type length: integer
    """
    __slots__ = ["message", "max", "min"]

    def __init__(self, min, max, message=None):
        if message:
            self.message = message
        else:
            self.message = "Length must be between {0} and {1} characters.". \
                            format(min, max)
        self.min = min
        self.max = max
        super(MinMaxValidator, self).__init__()

    def __call__(self, target):
        if len(target.data) < self.min or len(target.data) > self.max:
            target.add_error({'message': self.message})




class RequiredValidator(object):
    """ Checks to make sure the user entered something.

    :param message: (optional) The message to present to the user upon failure.
    :type message: string
    """
    __slots__ = ["message"]

    def __init__(self, message=None):
        self.message = message if message else "A value is required"
        super(RequiredValidator, self).__init__()

    def __call__(self, target=None):
        if len(target.data) == 0:
            target.add_error({'message': self.message})


class EmailValidator(object):
    """ A direct port of the Django Email validator. Checks to see if an
    email is valid using regular expressions.
    """

    user_regex = re.compile(
        r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*$"  # dot-atom
        r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-\011\013\014\016-\177])*"$)',
        # quoted-string
        re.IGNORECASE)
    domain_regex = re.compile(
        r'(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?$)'  # domain
        # literal form, ipv4 address (SMTP 4.1.3)
        r'|^\[(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}\]$',
        re.IGNORECASE)
    domain_whitelist = ['localhost']

    def __init__(self, message=None):
        self.message = message if message else "Entered value must be a valid"\
                                               " Email address"
        super(EmailValidator, self).__init__()

    def valid(self, value):
        """ A small breakout function to make passing back errors less
        redundant.
        """
        if not value or '@' not in value:
            return False

        user_part, domain_part = value.rsplit('@', 1)
        if not self.user_regex.match(user_part):
            return False

        if (not domain_part in self.domain_whitelist and
                not self.domain_regex.match(domain_part)):
            # Try for possible IDN domain-part
            try:
                domain_part = domain_part.encode('idna').decode('ascii')
                if not self.domain_regex.match(domain_part):
                    return False
                else:
                    return True
            except UnicodeError:
                return False

        return True

    def __call__(self, target):
        if self.valid(target.data):
            return None
        else:
            target.add_error({'message': self.message})


class Check(object):
    """ This object wraps a validator callable and is intended to be used in
    your `Form` subclass definition.

    :param callable validator: This is required to be a callable object
        that will carry out the actual validation. Many generic validators
        exist or you can roll your own.

    :param list args: A list of strings, or a single string,
        representing that _attr_name of the `Node` you would like passed
        into the validator. Once a validator is called this string will get
        resolved into a NamedTuple that will be passed into the validator
        callable.

    :param dict kwargs: Same as args above except it allows passing in node
        information as keyword arguments to the validator callable.

    `Check` objects are designed to be declared in your form subclass in one of
    two ways. Explicit.

    .. code-block:: python

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
    the _attr_name upon declaration explicitly. More on this in
    :ref:`Dynamically Adding Nodes`.

    Implicit declaration is a nice option for simple validators, and is simply
    syntactic sugar for the above syntax.

    .. code-block:: python

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
        and kwarg strings to their respective `Node` objects and replaces them
        with a KeyedTuple containing the submitted data and the Node object
        reference.
        :param form: A reference to the Form class that the check is being
        resolved to.
        :param data: The full form data dictionary submitted for validation.
        """
        if self.resolved:
            return

        # Process args
        for key, arg in enumerate(self.args):
            self.args[key] = form.get_by_attr(arg)

        # Process kwargs
        for key, val in self.kwargs.iteritems():
            self.kwargs[key] = form.get_by_attr(val)

        self.resolved = True

    def node_visited(self, visited):
        """ Used by piecewise validation to determine if all the Nodes involved
        in the validator have been "visited" and thus are ready for the
        validator to be run """

        if not self.resolved:
            raise ValueError("Check args are not resolved. This should not happen")

        """ Loop through the args. for each node, check if it's represented in
        the visited node list. if it is then then we're good to go"""
        for node in self.args:
            for name in node.get_list_names():
                if name in visited:
                    break
            else:  # if we didn't break, not enough info
                return False

        # Process kwargs
        for node in self.kwargs.itervalues():
            for name in node.get_list_names():
                if name in visited:
                    break
            else:  # if we didn't break
                return False

        # we identified at least one name in each node's collection of names
        return True

    def validate(self):
        """ Called by the validation routines. Allows the Check to specify
        parameters that will be passed to our Validation method.
        """

        if not self.resolved:
            raise ValueError("Check args are not resolved. This should not happen")

        try:
            # Run our validator
            return self.validator(*self.args, **self.kwargs)
        except TypeError as e:
            raise NotCallableException(
                "Validators provided must be callable, type '{0}'" +
                "instead. Caused by {1}".format(type(self.validator), e))
