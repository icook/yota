.. _validators:

=====================
Validators and Checks
=====================

.. py:currentmodule:: yota

Validators allow you to provide users feedback on their input through
structured, reusable callables. Validators can be supplied an arbitrary number of
inputs as well as dispatch information (errors, warnings, etc) to an arbitrary
number of output Nodes.

A validator should be a Python callable. The callable will be accessed through a
Check object that provides context on how you would like your validator to be
executed *in this given instance*. Checks are what provide your validation
callable with the data it is going to validate. Essentially they are context
resolvers, which is part of what allows Yota to be so dynamic.

When the validation callable is run it is supplied with a reference to a Node.
The submitted data that is associated with that :class:`Node` will be loaded
into the data attribute automatically. At this point, perhaps an example will help clarify.

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
attribute via the :meth:`Node.add_error`. This method is simply a wrapper
around appending to a list so that different ordering or filtering semantics
may be used if desired. The data can be put into this list is fairly flexible,
although a dictionary is recommended. If you are running a JSON based
validation method the data must by serializable, otherwise it may be anything
since it is merely passed into the rendering context of your templates. 

.. note:: If you wish to make use of `Special Key Values`_ you will be required to use dictionaries to return errors.

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

