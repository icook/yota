.. _renderers:

===========
Renderers
===========

.. py:currentmodule:: yota


.. _custom_templates:

Custom Templates
==========================
Most people end up needing to design templates different from the ones built in
at some point. Because of this Yota is setup for specifying a search path for
custom templates. By default Yota will only look at its own 
template directory. It is typical to add a search path that points somewhere
within your project. Yota will take the first template it finds that matches, so 
a simple way to ensure your custom templates are prioritized is to insert your path
first in the list. A typical example might look something like this:

.. code-block:: python

	import os
	from yota.renderers import JinjaRenderer

	JinjaRenderer.search_path.insert(0, os.path.dirname(os.path.realpath(__file__)) +
                                    "/assets/yota/templates/")
.. _template_sets:

Switching Template Sets
=======================
Yota provides potential for multiple default template sets. The default template
set is designed for use with Bootstrap 2.3.2, but a Bootstrap 3.0 implementation
can used by modifying the JinjaRenderer attribute templ_type to 'bs3'. More can
be read at :attr:`renderers.JinjaRenderer.templ_type`.

.. _rendering_engines:

Rendering Engines
==========================
By default Jinja2 is the renderer for Yota, however support for other renderes
is possible by setting the :attr:`Form._renderer` to a different class that
implements the proper interface. Currently the default and only option is
:class:`renderers.JinjaRenderer`, however other implementations should be easy to write.
The default Nodes :attr:`Node.template` property lacks a file extension and
expects the renderer to auto-append this before calling the template, thus
allowing the Node to work accross different renderers.

Renderers are invoked when a render method of a :class:`Form` is executed.
currently these include :meth:`Form.render` and :meth:`Form.validate_render`.
renderers were designed mainly to allow the interchange of template engines and
context gathering semantics. 

Renderer Interface
*********************
As of now only one method must be implemented by a Renderer: the render method.
It accepts two parameters, a list of Nodes to be rendererd in order and a
dictionary that contains the global context to include in every template context.
Looking at the source for JinjaRenderer will provide some guidence on how you
might write your own Renderer.

Switching Renderers
*********************
A standard pattern would be to set the Form class object :attr:`Form._renderer`
attribute allowing the attribute change to be effectively global. This would
normally be done in whatever setup function your web framework provides.

.. _jinjarenderer:

JinjaRenderer API
=================

.. autoclass:: yota.renderers.JinjaRenderer
    :members:
