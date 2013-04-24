.. Yota documentation master file, created by
   sphinx-quickstart on Sun Apr 21 04:43:03 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Yota: A simple, flexible HTML form library.
===========================================

Yota is a Python form library that aims to make generation of web forms fast yet flexible. It is designed to work with AJAX submission/validation or conventional submission methods. If you're trying to do something simple Yota's default should be well equipped for your needs, however it is still configurable enough to let you do more complex actions, even ones it wasn't originally designed to handle. Yota attempts to allow several ways to do things when it makes sense, but tries at all costs to avoid syntax that is overly confusing or non-obvious.

Yota was created due to the limited selection of mature AJAX form libraries out there. Deform being the most notable AJAX form libraries, and while it performs excellently for what it was designed to do, it always felt like it got in my way if I tried to do something it wasn't built for.

Basic Features
==============

* Simple declarative syntax for defining a Form schema
* Add elements and validators to your Form dynamically, freeing you from the bounds of a static Form schema.
* Flexible validation structure that allows an arbitrary number of inputs as well as outputs.
* Validation framework is designed to return results via JSON for client side rendering or directly to the rendering context for display after page submission.
* AJAX validation methods support piecewise validation for instant user feedback or on submit validation.
* Small, tested and documented. Under 1,000 lines of code without tests and documentation.
* Many small callback hooks built in limiting the amount of monkey-patching required to allow more custom functionality.

Contents
========

.. toctree::
    Form.rst
    Nodes.rst


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

