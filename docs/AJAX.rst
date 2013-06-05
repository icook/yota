================
AJAX Validation
================

.. py:currentmodule:: yota

Yota provides a basic JavaScript architecture in addition to specializatied
validation methods to enable easy construction of lightweight AJAX based Form
validation. Yota supports two main modes of AJAX based validation: piecewise and
on-submit. Piecewise validation attempts to validate a portion of the Form (only
the portions that it can) on some kind of trigger event, such as the user moving
to the next form element, or even keydown on a specific element.  On-submit is
just what it sounds like: when the form is submitted a server call is made and
the validation results are rendererd or a success action is executed. 

Piecewise Validation
=======================

