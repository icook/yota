================
AJAX Validation
================

.. py:currentmodule:: yota

Yota provides a JavaScript architecture in addition to specializatied
validation methods to enable easy construction of AJAX based Form validation.
Yota supports two main modes of AJAX based validation: piecewise and on-submit.
Piecewise validation attempts to validate a portion of the Form (only the
portions that the user has visited) on some kind of trigger event, such as the
user moving to the next form element, or keydown on a specific element.
On-submit is just what it sounds like: when the form is submitted an
asynchronous server call is made and the validation results are rendererd or a
success action is executed. These features allow you to give your user faster
feedback on what mistakes they made to ease the form filling process.

.. note:: The AJAX validator examples below rely on using the `id` attribute
    for a Node. This value is set by the default in :meth:`Node.set_identifiers`.

Server side implementation for AJAX validation is designed to be used with 
:meth:`Form.json_validate`. When a submission is detected (usually by detecting
a POST request), the method can be run to return the json
encoded validation results as the response. This response is then in turn
parsed by Yota's JavaScript library which can then execute callback functions
that you can design. To a user of the library, the implementation differeneces
of on-submit and piecewise are minor.

.. note:: Yota's JavaScript library is desinged as a jQuery plugin, and as such jQuery is
    also required to use these features.

As is classic for jQuery plugins configuration information is passed to Yota's
library through an options object.

.. js:data:: options.render_error

This attribute should be a function. It is called whenever new information is
recieved about a Node. The status attribute dictates what action should be performed.

    :param string status: This dictates the type of new information that was
        recieved. The first state is "error", and this means the Node is recieving
        an error for the first time. Common actions would be to un-hide an error
        div, or something similar. The second state is "update". This means that an
        error is currently registered with a Node, however we've recieved another
        batch of error for that Node. The errors are not necessarily different than
        the current errors. Finally, "no_error" indicates that there is no longer
        an error at this Node, and error messages should be removed. This will only
        be called if there is currently an error registered at the Node.

    :param object ids: This is the return information from the
        :meth:`Node.json_identifiers` function for the Node with which the error is
        being registered. It was intented to connect the rendering context that
        generates the DOM to your JavaScript that will be injecting into the DOM.

    :param object data: This is the json encoded :attr:`Node.errors` that
        should be populated by your validators. More about this can be found in
        the Node documentation, or the Validation documentation.

.. js:data:: options.render_success

This attribute should be a function. It is called when the form submission
succeeds, or rather it doesn't block. More information on blocking can be found
in the Validators section.

    :param object data: This is information directly generated from your
        :meth:`Form.success_header_generate` function. It is setup to display
        some sort of message that applies to the entire form such as an error
        working with the database, or proper submission of the data. In
        addition, some special key values can be set to trigger the execution
        of builtin convenience methods, such as redirection of the browser.
        More on this in Success Actions.

    :param object ids: This is the return information from the
        :meth:`Node.json_identifiers` function **for the start Node**. It was
        intented to connect the rendering context that generates the DOM to your
        JavaScript that will be injecting into the DOM.

.. js:data:: options.piecewise 

Whether or not this form should be processed in a piecewise fashion. The
default Node teamplte form_open will automatically populate this option when
you put 'piecewise' in your global context.

Success Actions
=======================
As was touched on in the JavaScript render_success function above, the method
:meth:`Form.success_header_generate` can be overriden to perform common post
submission actions, or to pass information that you may want to use in your
render_success function. The default render_success method will look for a
'message' key in the return value and display this in a Bootstrap success
alert, or do nothing if this key is not present. All actions are performed upon
successful submission, but prior to the ``render_success`` method being called.
A simple example is shown below.

.. code-block:: python
    :emphasize-lines: 5,6

    class MyForm(yota.Form):
        first = EntryNode(title='First name',
                            validator=Check(MinLengthValidator(5)))

        def success_header_generate(self):
            return {'message': 'Thanks for your submission!'}

Or if we wanted to redirect the user after submitting the form:

.. code-block:: python
    :emphasize-lines: 5,6

    class MyForm(yota.Form):
        first = EntryNode(title='First name',
                            validator=Check(MinLengthValidator(5)))

        def success_header_generate(self):
            return {'redirect': 'http://google.com/'}

Information on the avilible special post-submission actions are below.

Redirection
~~~~~~~~~~~~~~~~~~~~~~
Include the key 'redirect' in your return dictionary and the browser will
be sent to the url specified via method ``window.location.replace``.

Google Analytics Logging
~~~~~~~~~~~~~~~~~~~~~~~~
Under the key 'ga_run' return a list or tuple of four values, matching the four
values used in Google Analytics API function ``ga``. More information can be
found at the URL below.

https://developers.google.com/analytics/devguides/collection/analyticsjs/events

Clear Form Elements
~~~~~~~~~~~~~~~~~~~~~~~~
Pass the key 'clear_element' equal to True and upon submission all input fields
in the form will be reset.

Custom Action
~~~~~~~~~~~~~~~~~~~~~~~~
Include the key 'custom_success' as a string of valid JavaScript and it will be
evaled for you.

On-Submit Validation
=======================
A simple on submit validation should be very simple if you're sticking with the
default Nodes. These Nodes are already setup to pass the required error div ids
and element ids to the client using the default render_error function in Yota's
JavaScript library, so all you really need to do is set the global context key
'ajax' to equal True. This activates the JavaScript library.

Piecewise Validation
=======================
On-Submit validation only gives the user feedback when he has submitted the
Form, but what if we want to provide more instant feedback? Piecewise validation
allows us to fire off a server request to validate the form as we're filling it
out based on any JavaScript based trigger.

The server side of this implementation is almost identical to On-Submit
validation except that you want to pass the key 'piecewise' to the
g_context. Again, this simply triggers the JavaScript library to behave
slightly different. All builtin Nodes are designed to work out of the box with
the default AJAX callback functions.

Validation Tiggers
~~~~~~~~~~~~~~~~~~
A per-Node attribute 'piecewise_trigger' allows you to
set when you would like the Form to be submitted for incremental validation.
This can be any JavaScript event type that your input field supports, and
defaults to "blur". Common values may be click, change, dblclick, keyup or
keydown.

These event triggers are activated when the Yota jQuery plugin is initially
called. It scans all input fields in your Form and attaches an AJAX submit
action to the input element based on the value of the attribute
"data-piecewise". In the default Nodes this is set by the attribute
"piecewise_trigger" as can be seen in the code of the entry.html default template.

.. code-block:: html
    :emphasize-lines: 3

    {% extends base %}
    {% block control %}
    <input data-piecewise="{{ piecewise_trigger }}"
        type="text"
        id="{{ id }}"
        value="{{ data }}"
        name="{{ name }}"
        placeholder="{{ placeholder }}">
    {% endblock %}

