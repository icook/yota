.. ref:_form

===========
Using Forms
===========

.. py:currentmodule:: yota

.. _simple_form:

A Simple Form
=============

This is the core of Yota's functionality. To create a Form with Yota you must
inherit from the From superclass like in the following example.

.. code-block:: python

    from yota import Form
    from yota.nodes import *

    class PersonalForm(Form):

        first = EntryNode()
        last = EntryNode()
        address = EntryNode()
        submit = SubmitNode(title="Submit")

Forms are simply a collection of Nodes and Checks. The Checks drive validation of the Form and will be talked about next, while the Nodes drive rendering. Conceptually Nodes can be thought of as a single input section in your form, but it can actually be anything that is destined to generate some HTML or Javascript in your Form. For example you may wish to place a header at the beginning to the Form even though it isn't used for any data entry. Most keyword arguments passed to a Node are passed directly to their rendering context, and thus their use is completely up to user choice. More information on Nodes can be found in the :doc:`Nodes` documentation section. Your new Form class inherits lots of functionality for common tasks such as rendering and validation.

To render our Form we can call the :meth:`Form.render` function on an instance of our Form object::

    >>> personal = PersonalForm()
    >>> personal.render()
    '<form method="post">
    ...
    </form>'

As talked about in the Node documentation, each Node by default has an
associated template that is used to render it. The render function essentially
passes the list of Nodes in the Form onto the Renderer. Most renderers will
render each each Node's template and append them all together. In addition to
the Nodes that you have defined in your subclass, a Node for the beginning and
end of your Form will automatically be injected. The is a convenience that can
be disabled by setting the :attr:`Form.auto_start_close` to False. We
can see this functionality in action in the below example::

    >>> form = PersonalForm()
    >>> for node in form._node_list:
    ...     print node._attr_name
    ... 
    start
    first
    last
    address
    submit
    close

Even though 'first' was our first element in the Form and 'submit' was our last,
the Nodes 'start' and 'close' have been prepended and appended respectively. By
default these Nodes load from templates 'form_open.html' and 'form_close.html',
however these values can be easily overridden, as can the entire start and close
Nodes. For more information see the :attr:`Form.start`, 

Validation Intro
================

To add some validation to our Form we need to create a Check. Checks are just containers for Validators and hold information about how the Validator should be executed. The below code will add a Check for the 'first' Node to ensure a minimum length of 5 characters.

.. code-block:: python
    :linenos:
    :emphasize-lines: 8

    from yota import Form
    from yota.nodes import *
    from yota.validation import 

    class PersonalForm(Form):

        first = EntryNode()
        _first_valid = Check(MinLengthValidator(5), 'first')
        last = EntryNode()
        address = EntryNode()
        submit = SubmitNode(title="Submit")

The constructor prototype may help provide some reference for the explaination:

.. code-block: python

    Check(validator, \*attr_args, \*\*attr_kwargs)

When you define a Check object you are essentially specifying a Validator that needs to be run when the Form data is validated, and the information that needs to be passed to said Validator. Attr_args and attr_kwargs should be strings that define what data will get passed into the Validator at validation time. For instance in the above example that data that was entered for the 'first' Node will get passed to the validator. More information on Checks and Validators can be found on the :doc:`Validators` page.

Changing Rendering Engines
==========================
By default Jinja2 is the renderer for Yota, however support for other renderes
is possible by setting the :attr:`Form._renderer` to a different
implementation of the :class:`Renderer` class. The default is
:class:`JinjaRenderer`. A standard pattern would be to set the Form
class object _renderer attribute allowing the attribute change to be effectively
global. This would normally be done in whatever setup function your web
framework provides.


API
===========

.. autoclass:: Form
    :members:
    :private-members:
