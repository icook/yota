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
Most Node definitions are quite simple, with the majority simply changing the template being used. More complex Node semantics are availible by overriding some of their built in methods, such as :meth:`Node.resolve_data` or :meth:`Node.set_identifiers`. These are all described in detail in the API documentation, but some examples will be given here of how you might wish to use these methods.

resolve_data
****************************
The default Node implementation assumes that your Node only contains one input,
and as such its data output is assumed to be tied directly to this single input.
The :meth:`Node.set_identifiers` method defines a defualt implementation for naming
your input field. This name is then used to pick out the data that is associated
with this Node. But say your Node includes multiple input fields, perhaps you
have a date picker. A simple template may look like this:

.. code-block:: html

    Month: <input type="text" name="{ name }_month" placeholder="Month" /><br />
    Day: <input type="text" name="{ name }_day" placeholder="Day" /><br />
    Year: <input type="text" name="{ name }_year" placeholder="Year" /><br />

Now of course the :meth:`Node.resolve_data` will fail to find anything associated
with "name" since it doesn't exist, and instead an implementation may look
something like this.

.. code-block:: python
    
    def resolve_data(self, data):
        """ Resolve data should always throw a FormDataAccessException upon not
        finding data, as this is critial for piecewise validation to continue
        functioning """
        try:
            day = data[self.name + '_day']
            month = data[self.name + '_month']
            year = data[self.name + '_year']
        except KeyError:
            raise FormDataAccessException

        """ In case they enter something out of bounds """
        try:
            return datetime.date(year, month, day)
        except ValueError:
            return None

Now aside from our crappy looking form, and some lack of bound specificity
everything is peachy.

set_identifiers
****************************
This should be pretty self explanatory. When the Node is created set_identifiers
is called to setup some unique names to be used in the template. Perhaps you'd
like a different semantic for automatically titling your date pickers?

.. code-block:: python

    def set_identifiers(self, parent_name):
        super(MySuperSpecialNode, self).set_identifiers(parent_name)
        if not hasattr(self, 'title'):
            self.title = self._attr_name.capitalize() + " Very Special"

.. py:currentmodule:: yota

Builtin Nodes
=====================


.. autoclass:: yota.nodes.BaseNode
.. autoclass:: yota.nodes.NonDataNode
.. autoclass:: yota.nodes.ListNode
.. autoclass:: yota.nodes.RadioNode
.. autoclass:: yota.nodes.CheckGroupNode
.. autoclass:: yota.nodes.ButtonNode
.. autoclass:: yota.nodes.EntryNode
.. autoclass:: yota.nodes.TextareaNode
.. autoclass:: yota.nodes.SubmitNode
.. autoclass:: yota.nodes.LeaderNode

Node API
===========

.. autoclass:: Node
    :members:
    :undoc-members:
    :private-members:
