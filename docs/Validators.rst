.. _validators:

=====================
Validators and Checks
=====================

.. py:currentmodule:: yota

Validators allow you to provide users feedback on their input through
structured, reusable callables. Validators can be sent an arbitrary number of
inputs as well as dispatch information (errors, warnings, etc) to an arbitrary
number of Nodes.

A validator should be a Python callable that conforms to a specific standard so
that Yota knows how to interact with it.  The callable will be accessed through
a Check object that is provided as a class attribute. Checks provide the context
resolution that is required to run your validator, that is, they allow you to
specify which Node data should go into the validation callable. When the
validation callable is run it is supplied with a NamedTuple for each Node that
you asked to be passed in via your `Check` object. At this point, perhaps an
example will help clarify:::

    import yota

    def MyValidator(text):
        if len(text) > 5:
            return text.node, {'message': "You're text is too long!"}

    class MyForm(yota.Form):
        name = yota.nodes.EntryNode()
        _name_check = yota.validators.Check(MyValidator, 'name')

In the above exmaple we made a simple validator that throws an error if your
input value is longer than 5 characters. You can see the creation of the Check
in the Form declaration supplies 'name'. This is indicating the name of the Node
that you would like to supply to the Validator as input. Later when the
validator is to be called the string is replaced by a NamedTuple.  The named
tuple has two attributes: node and data. Node will be a reference to the actual
:class:`Node` instance while data is populated with the submission data associated with
that `Node`. This allows you to write a validator that accepts an arbitrarily
large amount of data with which to generate an output in what is hoped to be a
convenient and simple syntax.

Return Expectations
====================

Validators are expected to return either a single tuple or a list of tuples, or
None. None indicates no validation message to be transferred, while a tuple or
list of tuples declare the Node(s) to generate a message for. The tuples must
contain a target node as their first parameter and a dictionary of validation
results as the second parameter. Again, this can be seen in the above exmaple.
There are a couple special attributes that can be defined in this dictionary,
but these will be discussed a little later. How this data is used varies
slightly depending on the validation method used.

Validator Execution
=====================

With the regular form validation method `Form.validate_render` the data will
get passed directly to the `Node` rendering context as the ``error`` attribute
when the form is re-rendered after page submit. In your `Node` template, the
error can then be used for anything related to rendering and will contain
everything in the dictionary.

With either the piecewise JSON validation method or the regular JSON validation
method the data will get translated into JSON. This JSON string is designed to
be passed back via an AJAX request and fed into Yota's thing JacaScript library,
although could be used in other ways. Details about this functionality are in
the piecewise documentation section.

Special Key Values
=====================

|  **Block**
| If set to False the validation message will not prevent the form from submitting. Since the block value is actually something passed back from Yota at validation time, the actual action to be taken is up to the user. As might be expected, a single blocking validator will cause the block flag to return true. This is useful for things like notification of password strength, etc.

.. py:module:: yota

Check API
===========

.. autoclass:: Check
    :members:

