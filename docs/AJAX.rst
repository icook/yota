================
AJAX Validation
================

.. py:currentmodule:: yota

Yota provides some basic JavaScript architecture in addition to specializatied
validation methods to enable easily building lightweight AJAX based Form
Validation. Yota supports two main modes of AJAX based validation: piecewise
and on-submit. Piecewise validation attempts to validation a portion of the Form
(only the portions that it can) on some kind of trigger event, such as the user
moving to the next form element, or even keydown on a specific element.
On-submit is just what it sounds like: when the form is submitted a server call
is made and the validation results are rendererd. The validation methods and
JavaScript are discussed below.


