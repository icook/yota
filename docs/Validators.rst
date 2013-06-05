.. _validators:

=====================
Validators and Checks
=====================

.. py:currentmodule:: yota

Validators allow you to provide users feedback on their input through
structured, reusable callables. Validators can be sent an arbitrary number of
inputs as well as dispatch information (errors, warnings, etc) to an arbitrary
number of output Nodes.

A validator should be a Python callable. The callable will be accessed through a
Check object that provides context on how you would like your validator to be
executed *in this given instance*. Checks are what provide your validation
callable with the data it is going to validate. When the validation callable is
run it is supplied with a reference to a Node. The submitted data that is
associated with that :class:`Node` will be loaded into the data attribute. At
this point, perhaps an example will help clarify.

.. code-block:: python
    import yota

    def MyValidator(text):
        if len(text.data) > 5:
            test.add_error({'message': "You're text is too long!"})

    class MyForm(yota.Form):
        name = yota.nodes.EntryNode()
        _name_check = yota.validators.Check(MyValidator, 'name')

In the above exmaple we made a simple validator that throws an error if your
input value is longer than 5 characters. You can see the creation of the Check
instance in the Form declaration supplies the string 'name'. This is indicating
the _attr_name of the Node that you would like to supply to the Validator as
input. Later when the validator is to be called the string is replaced by a
refernce to a :class:`Node` with the specified :attr:`Node._attr_name`. The method behind this
maddness is that it allows for dynamically adding Nodes at and up until
vaildation time, as well as dynamic injection of validation rules themselves.
In addition your validation methods can now request as much data as you'd like,
and subsequently can disperse errors to an arbitrary number of :class:`Node`.

Return Semantics
====================

Validators need not return anything explicitly, but instead provide output by
appending error information to one of their Nodes errors list attribute. The
data that is put into this list is fairly flexible, although a dictionary is
recommended. If you are running a JSON based validation method the data must by
serializable, otherwise it may be anything since it is merely passed into the
rendering context of your templates. 

.. note:: If you wish to make use of `Special Key Values`_ you will be required to use dictionaries to return errors.

Validator Execution
=====================

With the regular form validation method :meth:`Form.validate_render` the values after
validation are preserved completely and passed into the rendering context. In
your :class:`Node` template, the error can then be used for anything related to
rendering and will contain exactly what was returned by your validator.

With either the piecewise JSON validation method or the regular JSON validation
method the data will get translated into JSON. This JSON string is designed to
be passed back via an AJAX request and fed into Yota's thing JacaScript library,
although could be used in other ways. Details about this functionality are in
the piecewise documentation section.

Special Key Values
=====================

| **Block**
| If set to False the validation message will not prevent the form from submitting. Since the block value is actually something passed back from Yota at validation time, the actual action to be taken is up to the user. As might be expected, a single blocking validator will cause the block flag to return true. This is useful for things like notification of password strength, etc.

.. py:module:: yota

===========
Check API
===========

.. autoclass:: Check
    :members:

