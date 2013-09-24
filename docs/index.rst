.. Yota documentation master file, created by
   sphinx-quickstart on Sun Apr 21 04:43:03 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Yota: Flexible forms with asynchronous validation
=================================================
.. py:module:: yota

Yota is a Python form generation library with the following unique features:

+ Easy integration of realtime validation. Trigger a server side form
  validation with any JavaScript event on your input fields. (Client side in
  planning)

+ Dynamic form structures allow for complex forms with on the fly changes.
  Inject different input fields or validation methods into a specific instance
  of your Form where needed.

+ Default themed with Bootstrap, allowing you to quickly throw together useful
  forms that look nice.

In addition to these features, Yota also includes most of the features that
you would see with other form libraries.

+ Simple declarative syntax for defining form validation and layout

+ Customizable template driven schemas

+ Ability to operate with almost any framework and use any rendering engine.
  (Default is jinja2)

Philosophically Yota aims to have a ton of flexibility, since designing
powerful webforms is infrequently a cookie cutter operation. This was the main
problem the designers had with other libraries is that they ended up getting in
the way if they wanted to do anything abnormal. At the same time however it is
important that sensible default be easy to use and implement, making the
creation of common forms trivial and lowering the inital learning curve.

Overall Architecture
====================

Yota allows you to create Forms quickly by declaring a class that is made up of
Nodes and Checks. Nodes drive the rendering of your form while Checks drive
validation of user input. Yotas power is derived from its integration of server
side and client side components, and a growing set of quality default Nodes and
Validators.

|  :doc:`Form <Form>`
|  The primary method of interaction with Yota, the Form class acts as a
    structure to contain all of the information about your Forms structure and
    configuration. Forms are usually just a collection of Nodes and Checks with
    some configuration data. Most method calls will be made on Form objects.

|  :doc:`Nodes <Nodes>`
|  Nodes are the actual bits that make up your forms output. Nodes link
    together rendering templates and neccessary context information. Nodes are very
    abstract, and could be used to render anything, although most render form
    elements.  The Forms attempts to make a minimum of assumptions about the Nodes
    attributes.

|  :doc:`Validators and Checks <Validators>`
|  Checks form the bridge between your Nodes and your validators.  Validators
    are supplied with the names of Nodes that are used in the actual Validation
    callable. At validation time these names are resolved to the actual Node
    reference.

|  :ref:`renderers`
|  Renderers provide a pluggable interface through which you can render your
    form. This allows interchange of different templating engines, etc.


Contents
========

.. toctree::
    Form.rst
    Nodes.rst
    Validators.rst
    Renderers.rst
    AJAX.rst


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

