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

On-Submit Validation
=======================
Server side implementation for on-submit validation is designed to be used with 
:meth:`Form.json_validate`. When a submission is detected, return the json
encoded validation results as the response.

On the client side the interaction is setup to be handled with the jQuery form
plugin through a thin wrapper that accepts two JavaScript callbacks. The first
callback is responsible for rendering or hiding validation messages. It is
called once for every Node in your Form with a boolean validation status
and a JSON object that is the serialized :attr:`Node.errors` attribute.

The other callback is simply the success action, which would frequently involve
rendering a success message of some kind and possibly navigating the user to the
next page. An invocation example of this wrapper is below.

Piecewise Validation
=======================
On-Submit validation only gives the user feedback when he has submitted the
Form, but what if we want to provide more instant feedback? Piecewise validation
allows us to fire off a server request to validate the form as we're filling it
out based on any JavaScript based trigger.

The server side of this implementation is almost identical to On-Submit
validation except that you want to pass :meth:`Form.json_validate` the keyword
argument piecewise=True. This tells the validation method to simply ignore
errors in which there isn't the correct data to run the validator, as this is
expected when submitting only portions of the Form.

The client side of 
