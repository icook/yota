.. image:: _static/arch.png

|  :doc:`Form <Form>`
|  The primary method of interaction with Yota, the Form class acts as a structure to contain all of the information about your Forms structure and configuration. Forms are usually just a collection of Nodes and Checks with some configuration data. Most method calls will be made on Form objects.

|  :doc:`Nodes <Nodes>`
|  Nodes are the actual bits that make up your form. By default a Node has a template attribute that the Renderer picks up in its rendering method as well as context information to be passed into the rendering template. Despite this default, a Node is very abstract, and could be implemented quite differently.  The Form class above it attempts to make a minimum of assumptions about the Nodes attributes.

|  :doc:`Validators and Checks <Validators>`
|  Checks form the bridge between your submission data and your validators. Validators are supplied with the names of Nodes that are used in the actual Validation callable. At validation time these names are resolved to a tuple containing the actual Node reference as well as your submission data.

|  :doc:`Renderers <Renderers>`
|  Renderers provide a pluggable interface through which you can render your form. This allows interchange of different templating engines, etc.


Contents
========

.. toctree::
    Form.rst
    Nodes.rst
    Validators.rst


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

