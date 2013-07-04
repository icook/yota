.. _validators:

=====================
Validators and Checks
=====================

.. py:currentmodule:: yota

Validators allow you to provide users feedback on their input through
structured, reusable callables. Validators can be supplied an arbitrary number of
inputs as well as dispatch information (errors, warnings, etc) to an arbitrary
number of output Nodes.

Using Validators In Your Form
=============================

Validators are generally added into your Form schema in a way similar to adding
Nodes; that is, by declaring attributes in your Form definition. There is a
long syntax that is more explicit as well as a shorthand that can add
convenience for simple validators. The explicit declaration can be seen below
through the definition of a Check.

.. code-block:: python
    :emphasize-lines: 5

    class MyForm(yota.Form):
        # This syntax shortens up the above explicit syntax for simple
        # validators
        first = EntryNode(title='First name')
        _first_valid = Check(MinLengthValidator(5), 'first')

The syntax above defines a single EntryNode and an associated validator that
ensures the entered value is at least 5 characters long. This is done through
the declaration of a :class:`Check` object. The Check accepts the actual
validator as its first argument, followed by the names of Nodes that you will
be validating. The above example binds our `MinLengthValidator` to a Node with
the attribute name 'first'. Later when we try to validate the Form the string
'first' will be used to lookup our Node and supply the appropriate information
to the validator method. Nodes in Yota are identified by their attribute name
as given in the class declaration. However, If you later add a `Node`
dynamically it will need to specify the _attr_name attribute upon declaration
explicitly. More on this in :ref:`Dynamically Adding Nodes`.

The above syntax gives us some nice power. We can supply that validation method
with as many Nodes as we would like in a clear way. But what if we want to
write a bunch of validators that only validate a single Node? Then the above is
quite verbose, and below shows an implicit declaration that is a nice option
for simple validators, and is just syntactic sugar for the above syntax.

.. code-block:: python
    :emphasize-lines: 6, 10, 15, 19, 20

    class MyForm(yota.Form):
        # This syntax shortens up the above explicit syntax for simple
        # validators. An arg of 'first' will automatically be added to the
        # Check object for you.
        first = EntryNode(title='First name',
                            validator=Check(MinLengthValidator(5)))

        # This even more brief syntax will automatically build the Check
        # object for you since it's just boilerplate at this point
        last = EntryNode(title='Last name', validator=MinLengthValidator(5)

        # This syntax however is just like above. Be aware that your
        # attribute name will not be automatically added since your
        # explicitly defining args
        address = EntryNode(validator=
                    Check(MinLengthValidator(9), 'address'))

        # In addition, you can specify a list of validators, or a tuple
        addr = EntryNode(title='Address', validator=[MinLengthValidator(5),
                                                     MaxLengthValidator(25)])

.. note:: If neither kwargs or args are specified and cannot be implicitly determined
    an exception will be thrown.

Validator Execution
=====================

With the regular form validation method :meth:`Form.validate_render` the error
values after validation are maintained in `errors` and passed into the rendering
context. In your :class:`Node` template, the error can then be used for
anything related to rendering and will contain exactly what was returned by
your validator.

With either the piecewise JSON validation method or the regular JSON validation
method the data will get translated into JSON. This JSON string is designed to
be passed back via an AJAX request and fed into Yota's JacaScript jQuery plugin,
although it could be used in other ways. Details about this functionality are in
the AJAX documentation section.

To continue our example series above, we may now try and execute a validation
action on our Form. For this example we will use a Flask view, although the
concepts should be fairly obvious and transfer to most frameworks easily.

.. code-block:: python
    :emphasize-lines: 6, 10, 15, 19, 20

    class MyForm(yota.Form):
        # Our same form definition as above but stripped of the now un-needed
        # comments
        first = EntryNode(title='First name',
                            validator=Check(MinLengthValidator(5)))
        last = EntryNode(title='Last name', validator=MinLengthValidator(5)
        address = EntryNode(validator=
                    Check(MinLengthValidator(9), 'address'))

    # In Flask routes are declared with annotations. Basically mapping a URL to
    # this method
    @app.route("/ourform", methods=['GET', 'POST'])
    def basic():
        # Create an instance of our Form class
        form = MyForm()
    
        # When the form is submitted to this URL (by default forms submit to
        # themselves)
        if request.method == 'POST':
            # Run our convenience method designed for regular forms
            # 'success' if validation passed, 'out' is the re-rendering of the form
            success, out = form.validate_render(request.form)

            # if validation passed, we should be doing something
            if success:
                # Load up our validated data
                data = form.get_by_attribute()

                # Create a pretend SQLAlchemy object. Basically, we want to try
                # and save the data somehow...
                res = User(first=data['first'],
                           last=data['last'],
                           address=data['address']) 

                # Attempt to save our changes
                try:
                    DBSession.add(new_user)
                    DBSession.commit()
                except (sqlalchemy.exc, sqlalchemy.orm.exc) as e:
                    # An error with our query has occurred, change the message
                    # and update our rendered output
                    out = form.update_success(
                        {'message': ('An error with our database occurred!')})
        else:
            # By default we just render an empty form
            out = form.render()
    
        def success_header_generate(self):
            return {'message': 'Thanks for your submission!'}
    
        return render_template('basic.html',
                                form=out)

Making Custom Validators
========================
A validator should be a Python callable. The callable will be accessed through a
Check object that provides context on how you would like your validator to be
executed *in this given instance*. Checks are what provide your validation
callable with the data it is going to validate. Essentially they are context
resolvers, which is part of what allows Yota to be so dynamic.

When the validation callable is run it is supplied with a reference to a Node.
The submitted data that is associated with that :class:`Node` will be loaded
into the data attribute automatically. At this point, perhaps an example will
help clarify.

.. code-block:: python

    import yota

    def MyValidator(node_in):
        if len(node_in.data) > 5:
            node_in.add_error({'message': "You're text is too long!"})

    class MyForm(yota.Form):
        test_node = yota.nodes.EntryNode()
        _test_check = yota.validators.Check(MyValidator, 'test_node')

In the above exmaple we made a simple validator that throws an error if your
input value is longer than 5 characters. You can see the creation of the Check
instance in the Form declaration supplies the string 'test_node'. This is indicating
the name of the Node that you would like to supply to the Validator as
input.

.. note:: In Yota, all Nodes are uniquely identified by an attribute
    _attr_name. This gets automatically set to the value of the attribute you
    assigned the Node to in your Form declaration.

Later when the validator is to be called the string is replaced by a refernce
to a :class:`Node` with the specified :attr:`Node._attr_name`. The method
behind this maddness is that it allows for dynamically adding Nodes at and up
until vaildation time, as well as dynamic injection of validation rules
themselves. In addition your validation methods can now request as much data
as you'd like, and subsequently can disperse errors to any Nodes they are
supplied with.

Return Semantics
====================

Validators need not return anything explicitly, but instead provide output by
appending error information to one of their supplied Node's errors list
attribute via the method :meth:`Node.add_error`. This method is simply a wrapper
around appending to a list so that different ordering or filtering semantics
may be used if desired. The data can be put into this list is fairly flexible,
although a dictionary is recommended. If you are running a JSON based
validation method the data must by serializable, otherwise it may be anything
since it is merely passed into the rendering context of your templates. The
default templates are setup to look for a dictionary with a single key
'message' which will be printed. Looking at a builtin validator should provide
additional clarity.

.. code-block:: python

    class IntegerValidator(object):
        """ Checks if the value is an integer and converts it to one if it is

        :param message: (optional) The message to present to the user upon failure.
        :type message: string
        """
        # A minor optimization that is borderline silly
        __slots__ = ["message"]

        def __init__(self, message=None):
            self.message = message if message else "Value must only contain numbers"
            super(IntegerValidator, self).__init__()

        def __call__(self, target):
            # This provides a conversion as well as a validation
            try:
                target.data = int(target.data)
            except ValueError:
                target.add_error({'message': self.message})

.. note:: If you wish to make use of `Special Key Values`_ you will be required to use dictionaries to return errors.

Special Key Values
=====================
| **Block**
| If set to False the validation message will not prevent the form from
    submitting.  As might be expected, a single blocking validator will cause
    the block flag to return true. This is useful for things like notification
    of password strength, etc.

.. py:module:: yota

Builtin Validators
=====================
The default pattern for builtin Validators in Yota is to return a dictionary
with a key 'message' containing the error. This is also the pattern that the
builtin :class:`Nodes`'s except when rendering errors, and therefore is the
recommended format when building your own validators.

.. autoclass:: yota.validators.MinLengthValidator
.. autoclass:: yota.validators.MaxLengthValidator
.. autoclass:: yota.validators.MinMaxValidator
.. autoclass:: yota.validators.RequiredValidator
.. autoclass:: yota.validators.EmailValidator
.. autoclass:: yota.validators.MatchingValidator
.. autoclass:: yota.validators.IntegerValidator

Check API
===========

.. autoclass:: Check
    :members:

