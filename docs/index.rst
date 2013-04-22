.. Yota documentation master file, created by
   sphinx-quickstart on Sun Apr 21 04:43:03 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Yota: A simple, flexible HTML form library.
===========================================

Yota is a Python form library that aims to make generation of HTML forms fast yet flexible. If you're trying to do something simple Yota's default should be well equipped for your needs yet it is still configurable enough to allow for complex AJAX forms with instant validation. Yota attempts to allow several ways to do things when it makes sense, but tries at all costs to avoid syntax that is overly confusing or non-obvious.

Basic Features
==============

* Simple declarative syntax for defining a Form schema
* Add elements and validators to your Form dynamically, freeing you from the bounds of a static Form schema.
* Flexible Validation structure that allows an arbitrary number of inputs as well as outputs.
* Built in Validation framework is designed to return results via JSON with examples for lightweight client side rendering.
* Small, well tested and documented. Under 1,000 lines of code.
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

