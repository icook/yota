===========
Nodes
===========

.. py:currentmodule:: yota

Nodes drive the actual rendering of your :class:`Form`. Internally a
:class:`Form` keeps track of a list of :class:`Node`'s and then passes them off
to the :class:`Renderer` when a render of the :class:`Form` is requested. Lets
look at a simple example Form as shown in the introduction:

.. code-block:: python

    from yota import Form
    from yota.nodes import *

    class PersonalForm(Form):

        first = EntryNode()
        last = EntryNode()
        address = EntryNode()
        submit = SubmitNode(title="Submit")

All of the attributes in the above class definition are special :class:`Node`'s.
Internally there is some trickery with metaclasses that remembers what order
they were declared in, and then stores the order, but this is not important to
understand for using them. The simplest Node is simply a reference to some kind
of rendering template (by default, Jinaj2) and some associated metadata.

Custom Nodes
===============================
Most Node definitions are quite simple, with the majority simply changing the template being used. More complex Node semantics are availible by overriding some of their built in methods, such as :meth:`resolve_data` or :meth:`set_identifiers`. These are all described in detail in the API documentation.    

.. py:currentmodule:: yota

API
===========

.. autoclass:: Node
    :members:
    :private-members:
