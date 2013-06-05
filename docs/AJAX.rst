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
just what it sounds like: when the form is submitted an asynchronous server call
is made and the validation results are rendererd or a success action is
executed. 

.. note:: The AJAX validator examples below rely on using the `id` value that is set by the default :meth:`Node.set_identifiers` as a way to find the Nodes.

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
rendering a success message of some kind and possibly navigating the user to
the next page. An invocation example of this wrapper is below making use of
jQuery. The chunk below is designed to be put into the start Node of our
:class:`Form` definition so that it has access to things like the Form id.

.. code-block:: javascript

    // onload of our page
    $(function () {

        // define our callback to handle a validation message
        var handle_ret = function (id, error, data) {
            // if there was a validation error registered
            if (error) {
                // create a bootstrap colored tooltip that looks nice
                if ($('#' + id).attr('data-error') != "true") {
                    $('#' + id).tooltip({title: data['message'],
                                          placement: 'right',
                                          trigger: 'manual'});
                    $('#' + id).tooltip('show');
                    $('#' + id).attr('data-error', "true");
                }
            } else {
                // remove the tooltip, there is now no error registered
                $('#' + id).tooltip('destroy');
                $('#' + id).attr('data-error', "false");
            }
        }

        // define a function that executes upon successful validation
        var handle_submit = function () {

        }

        // run our yota wrapper
        ajax_activate("{{ id }}", handle_ret, handle_submit);
    });


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

The client side is a bit more tricky. When the page is first loaded, a
JavaScript object is constructed that tracks the state of each input field. That
is, it tracks whether or not the user has tried to modify the field.
Whenever the trigger event for a field is executed then the fields state is
updated and a partial submission is performed. The partial submission submits
data only for fields that have been flagged as modified. Then the server side
proceeds to execute all the validators that it can and then returns the result
exactly like On-Submit validation does.

Below is a simple example of how you might use the piecewise validation in your start :class:`Form` Node.

.. code-block:: javascript

    // onload of our page
    $(function () {
        // initialize our tracking object
        window.visited = {};

        // setup our listeners
        $("#{{ id }}").find("[data-piecewise]").each(function() {
            var v = $(this).attr("name");
            visited[v] = false;
            var type = $(this).attr("data-piecewise")
            if (type == "blur") {
                $(this).blur(function() {
                    window.visited[v] = true;
                    $("#{{ id }}").ajaxSubmit(window.yota_ajax_options);
                });
            } else {
                $(this).keyup(function() {
                    window.visited[v] = true;
                    $("#{{ id }}").ajaxSubmit(window.yota_ajax_options);
                });
            }
        });
    });
