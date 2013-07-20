from yota.renderers import JinjaRenderer
from yota.processors import FlaskPostProcessor
from yota.nodes import LeaderNode, Node
from yota.validators import Check
import json
import copy


class TrackingMeta(type):
    """ This metaclass builds our Form classes. It generates the internal
    _node_list which preserves order of Nodes in your Form as declared. It also
    generates _validation_list for explicitly declared Check attributes in the
    Form """

    def __init__(mcs, name, bases, dct):
        """ Process all of the attributes in the `Form` (or subclass)
        declaration and place them accordingly. This builds the internal
        _node_list and _validation_list and is responsible for preserving
        initial Node order. """

        nodes = {}
        mcs._validation_list = []
        mcs._node_list = []
        for name, attribute in dct.items():
            # These aren't ordered Nodes, ignore them
            if name is 'start' or name is 'close':
                try:
                    attribute._attr_name = name
                except AttributeError:
                    raise AttributeError("start/close attribute is special and"
                        "should specify a Node to begin your form. Got type {0}"
                        "instead".format(type(name)))
                continue
            if isinstance(attribute, Node):
                attribute._attr_name = name
                nodes[attribute._create_counter] = attribute
                delattr(mcs, name)
            elif isinstance(attribute, Check):
                # if we've found a validation check
                attribute._attr_name = name
                mcs._validation_list.append(attribute)
                delattr(mcs, name)

        # insert our nodes in sorted order by there initialization order, thus
        # preserving order
        for i, attribute in sorted(nodes.items()):
            mcs._node_list.append(attribute)

_Form = TrackingMeta('_Form', (object, ), {})
class Form(_Form):
    """ This is the base class that all user defined forms should inherit from,
    and as such it is the main way to access functionality in Yota. It
    provides the core functionality involved with setting up and
    rendering the form.

    :param context: This is a context specifically for the special form open
        and form close nodes, canonically called start and close.

    :param g_context: This is a global context that will be passed to all nodes
        in rendering thorugh their rendering context as 'g' variable.

    :param start_template: The template used when automatically
        injecting a start Node. See :attr:`yota.Form.auto_start_close` for
        more information.

    :param close_template: The template used when automatically
        injecting a close Node. See :attr:`yota.Form.auto_start_close` for
        more information.

    :param auto_start_close: Dictates whether or not start and close
        Nodes will be automatically appended/prepended to your form. Note
        that this must be set via __init__ or your class definition since it
        must be set before __init__ for the Form is run.

    :param hidden: A dictionary of hidden key/value pairs to be injected
        into the form.  This is frequently used to pass dynamic form
        parameters into the validator.

    """

    __metaclass__ = TrackingMeta
    _renderer = JinjaRenderer
    """ This is a class object that is used to perform the actual rendering
    steps, allowing different rendering engines to be swapped out. More about
    this in the section :class:`Renderer` """
    _processor = FlaskPostProcessor
    """ This is a class that performs post processing on whatever is passed in
    as data during validation. The intended purpose of this was to write
    processors that translated submitted form data from the format of the web
    framework being used to a format that Yota expects. It also allows things
    like filtering stripping characters or encoding all data that enters a
    validator. """
    _reserved_attr_names = ('context', 'hidden', 'g_context', 'start_template',
                        'close_template', 'auto_start_close', '_renderer',
                        '_processor', 'name')
    name = None
    context = {}
    g_context = {}
    title = None
    auto_start_close = True
    start_template = 'form_open'
    close_template = 'form_close'

    def __init__(self, **kwargs):
        # A bit of a hack to copy all our class attributes
        for class_attr in dir(self):
            if class_attr in kwargs:
                continue
            att = getattr(self, class_attr)
            # We want to copy all the nodes as well as the list, this is a
            # succinct way to do it
            if class_attr in ['_node_list', '_validation_list']:
                setattr(self, class_attr, copy.deepcopy(att))
            # Private attributes are internal stuff..
            elif not class_attr.startswith('__'):
                # don't try to copy functions, it doesn't go well
                if not callable(att):
                    setattr(self, class_attr, copy.copy(att))

        # Set a default name for our Form
        if self.name is None:
            self.name = self.__class__.__name__

        # pass some attributes to start/close nodes
        self.context['name'] = self.name
        self.context['title'] = self.title

        # run our safety checks, set identifiers, and set local attributes
        for node in self._node_list:
            self._setup_node(node)

        # passes everything to our rendering context and updates params.
        self.context.update(kwargs)
        self.__dict__.update(kwargs)

        # Add our open and close form defaults
        if hasattr(self, 'start'):
            self._node_list.insert(0, self.start)
        else:
            if self.auto_start_close:
                self.insert(0, LeaderNode(template=self.start_template,
                                        _attr_name='start',
                                        **self.context))
        if hasattr(self, 'close'):
            self._node_list.append(self.close)
        else:
            if self.auto_start_close:
                self.insert(-1, LeaderNode(template=self.close_template,
                                           _attr_name='close',
                                           **self.context))

        # Add some useful global variables for templates
        default_globals = {'form_id': self.name}
        # Let our globals be overridden
        default_globals.update(self.g_context)
        self.g_context = default_globals

        # Initialize some general state variable
        self._last_valid = None
        self._last_raw_json = None

    def render(self):
        """ Runs the renderer to parse templates of nodes and generate the form
        HTML.

        :returns: A string containing the generated output.
        """

        return self._renderer().render(self._node_list, self.g_context)

    def _setup_node(self, node):
        """ An internal function performs some safety checks, sets attribute,
        and set_identifiers """
        try:
            if type(node._attr_name) is not str:
                raise AttributeError
        except AttributeError as e:
            raise AttributeError('Dynamically inserted nodes must have a _attr_name'
                                 ' attribute as a string. Please add it. ')

        if hasattr(self, node._attr_name):
            raise AttributeError( 'Attribute name {0} overlaps with a Form '
                                 'attribute. Please rename.'
                .format(node._attr_name))

        node.set_identifiers(self.name)
        setattr(self, node._attr_name, node)

    def _parse_shorthand_validator(self, node):
        """ Loops thorugh all the Nodes and checks for shorthand validators.
        After inserting their checks into the form obj they are removed from
        the node. This is because a validation may be called multiple times on
        a single form instance. """
        if hasattr(node, 'validators') and node.validators:
            # Convert a single callable to an iterator for convenience
            if callable(node.validators):
                node.validators = (node.validators, )

            for validator in node.validators:
                # If they provided a check add it, otherwise make the check
                # for them
                if isinstance(validator, Check):
                    # Just for extra flexibility, add the attr if they left it out
                    if not validator.args and not validator.kwargs:
                        validator.args.append(node._attr_name)
                    self._validation_list.append(validator)
                else:
                    # Assume only a single attr if not specified
                    new_valid = Check(validator, node._attr_name)
                    self._validation_list.append(new_valid)

            # remove the attribute so multiple calls doesn't break things
            delattr(node, 'validators')

    def insert_validator(self, new_validators):
        """ Inserts a validator to the validator list.

        :param validator: The :class:`Check` to be inserted.
        :type validator: Check """

        for validator in new_validators:
            # check to allow passing in just a check
            if not isinstance(validator, Check):
                raise TypeError('Can only insert type Check or derived classes')

            # append the validator to the list
            self._validation_list.append(validator)

    def insert(self, position, new_node_list):
        """ Inserts a :class:`Node` object or a list of objects at the
        specified position into the :attr:`Form._node_list` of the form.
        Index -1 is an alias for the end of the list.  After insertion
        the :meth:`Node.set_identifiers` will be called to generate
        identification for the :class:`Node`. For this to function,
        :attr:`Form._attr_name` must be specified for the node prior to
        insertion. """

        # check to allow passing in just a node
        if isinstance(new_node_list, Node):
            new_node_list = (new_node_list,)

        for i, new_node in enumerate(new_node_list):

            self._setup_node(new_node)

            if position == -1:
                self._node_list.append(new_node)
            else:
                self._node_list.insert(position + i, new_node)

    def insert_after(self, prev_attr_name, new_node_list):
        """ Runs through the internal node structure attempting to find
        a :class:`Node` object whos :attr:`Node._attr_name` is
        prev_attr_name and inserts the passed node after it. If
        `prev_attr_name` cannot be matched it will be inserted at the
        end. Internally calls :meth:`Form.insert` and has the same
        requirements of the :class:`Node`.

        :param prev_attr_name: The attribute name of the `Node` that you
            would like to insert after.
        :type prev_attr_name: string
        :param new_node_list: The :class:`Node` or list of Nodes to be
            inserted.
        :type new_node_list: Node or list of Nodes """

        # check to allow passing in just a node
        if isinstance(new_node_list, Node):
            new_node_list = (new_node_list,)

        # Loop through our list of nodes to find where to insert
        for index, node in enumerate(self._node_list):
            # found!
            if node._attr_name == prev_attr_name:
                for i, new_node in enumerate(new_node_list):
                    self._node_list.insert(index + i + 1, new_node)
                    setattr(self, new_node._attr_name, new_node)
                    new_node.set_identifiers(self.name)
                break
        else:
            # failover append if not found
            for new_node in new_node_list:
                self._node_list.append(new_node)

    def get_by_attr(self, name):
        """ Safe accessor for looking up a node by :attr:`Node._attr_name` """
        try:
            attr = getattr(self, name)
        except AttributeError:
            pass
        else:
            if isinstance(attr, Node):
                return attr
        raise AttributeError('Form attribute {0} couldn\'t be resolved to'
                             ' a Node'.format(name))

    def success_header_generate(self):
        """ Please see the documentation for :meth:`Form.error_header_generate`
        as it covers this function as well as itself. """
        pass

    def error_header_generate(self, errors, block):
        """ This function, along with success_header_generate allow you to give
        form wide information back to the user for both AJAJ validated forms
        and conventionally validated forms, although the mechanisms are
        slightly different. Both functions are run at the end of a successful
        or failed validation call in order to give more information for
        rendering.

        For passing information to AJAJ rendering, simply return a dictionary,
        or any Python object that can be serialized to JSON. This information
        gets passed back to the JavaScript callbacks of yota_activate, however
        each in slightly different ways. success_header_generate's information
        will get passed to the render_success callback, while
        error_header_generate will get sent as an error to the render_error
        callback under the context start.

        For passing information into a regular, non AJAJ context simply access
        the attribute manually similar to below.

        .. code-block:: python

            self.start.add_error(
                {'message': 'Please resolve the errors below to continue.'})

        This will provide a simple error message to your start Node. In
        practice these functions could also be used to trigger events and other
        interesting things, although that was not their intended function.

        :param errors: This will be a list of all other Nodes that have errors.
        :param block: Whether or not the form submission will be blocked.
        :type block: boolean

        .. note: By default this function does nothing.
        """
        pass

    def data_by_attr(self):
        """ Returns a dictionary of currently stored :attr:`Node.data`
        attributes keyed by :attr:`Node._attr_name`. Used for returning data
        after its been processed by validators. """

        ret = {}
        for node in self._node_list:
            ret[node._attr_name] = node.data
        return ret

    def data_by_name(self):
        """ Returns a dictionary of currently stored :attr:`Node.data`
        attributes keyed by :attr:`Node.name`. Used for returning data
        after its been processed by validators. """

        ret = {}
        for node in self._node_list:
            ret[node.name] = node.data
        return ret

    def _gen_validate(self, data, piecewise=False):
        """ This is an internal utility function that does the grunt work of
        running validation logic for a :class:`Form`. It is called by the other
        primary validation methods. """

        # Allows user to set a modular processor on incoming data
        data = self._processor().filter_post(data)


        # reset all error lists and data
        for node in self._node_list:
            node.errors = []
            node.data = ''
            node.resolve_data(data)
            # Pull out all our shorthand validators
            self._parse_shorthand_validator(node)

        # try to load our visited list of it's piecewise validation
        if '_visited_names' not in data and piecewise:
            raise AttributeError("No _visited_names present in data submission"
                                 ". Data is required for piecewise validation")
        elif piecewise:
            visited = json.loads(data['_visited_names'])

        # assume to be not blocking
        block = False
        # loop over our checks and run our validators
        for check in self._validation_list:
            check.resolve_attr_names(data, self)
            if piecewise is False or check.node_visited(visited):
                check.validate()
            else:
                # If even a single check can't be run, we need to block
                block = True

        # Run the one off validation method
        self.validator()

        # a list to hold Nodes that actually have errors
        error_node_list = []
        for node in self._node_list:
            # slightly confusing way of setting our block = True by
            # default
            if node.errors:
                error_node_list.append(node)

            for error in node.errors:
                block |= error.get('block', True)

        return block, error_node_list

    def json_validate(self, data, piecewise=False, raw=False):
        """ The same as :meth:`Form.validate_render` except the errors
        are loaded into a JSON string to be passed back as a query
        result. This output is designed to be used by the Yota
        Javascript library.

        :param piecewise: If set to True, the validator will silently
            ignore validator for which it has insufficient information. This
            is designed to be used for the AJAJ piecewise validation
            function, although it does not have to be.
        :type piecewise: boolean

        :param raw: If set to True then the second return parameter will be a
            Python dictionary instead of a JSON string
        :type raw: boolean

        :return: A boolean whether or not the form submission is valid and the
            json string (or raw dictionary) to pass back to the javascript side.
            The boolean is an anding of submission (whether the submit button was
            actually pressed) and the block parameter (whether or not any blocking
            validators passed)
        """

        # Allows user to set a modular processor on incoming data
        data = self._processor().filter_post(data)

        errors = {}
        """ We want to automatically block the form from actually submitting
        if this is piecewise validation. In addition if they are actually
        submitting then we want to run it as non-piecewise validation """
        if data.get('submit_action', 'false') != 'true' and piecewise:
            block, invalid = self._gen_validate(data, piecewise=piecewise)
            block = True
        else:
            block, invalid = self._gen_validate(data, piecewise=False)

        # loop over our nodes and insert information for the JS callbacks
        for node in invalid:
            errors[node._attr_name] = {'identifiers': node.json_identifiers(),
                                       'errors': node.errors}

        # if needed we should run our all form message generator and return
        # json encoded error message
        retval = {'block': block}
        if len(errors) > 0:
            header_err = self.error_header_generate(errors, block)
            if header_err:
                errors['start'] = {'identifiers': self.start.json_identifiers(),
                                   'errors': header_err}

        if not block:
            blob = self.success_header_generate()
            if blob:
                retval['success_blob'] = blob
            if hasattr(self, 'start'):
                retval['success_ids'] = self.start.json_identifiers()

        retval['errors'] = errors

        # Throw back a variable in the json if there is both a submit
        # and no blocking errors. The main purpose here is the allow
        # easy catching of success in the view code.
        if data.get('submit_action', 'false') == 'true' and not block:
            valid = True
        else:
            valid = False

        # Hold our return dictionary in memeory for easy editing later
        self._last_raw_json = retval

        # Return our raw dictionary if requested, otherwise serialize for
        # convenience...
        if raw:
            return valid, retval
        else:
            return valid, json.dumps(retval)

    def validate(self, data):
        """ Runs all the validators associated with the :class:`Form`.

        :return: Whether the validators are blocking submission and a list of
            nodes that have validation messages.
        """

        # Allows user to set a modular processor on incoming data
        data = self._processor().filter_post(data)
        block, invalid = self._gen_validate(data)

        return (not block), invalid

    def validate_render(self, data):
        """ Runs all the validators on the `data` that is passed in and returns
        a re-render of the :class:`Form` if there are validation errors,
        otherwise it returns True representing a successful submission. Since
        validators are designed to pass error information in through the
        :attr:`Node.errors` attribute then this error information is in turn
        availible through the rendering context.

        :param data: The data to be passed through the
            `Form._processor`. If the data is in the form of a dictionary
            where the key is the 'name' of the form field and the data is a
            string then no post-processing is neccessary.
        :type data: dictionary

        :return: Whether the validators are blocking submission and a re-render
            of the form with the validation data passed in.
        """

        # Allows user to set a modular processor on incoming data
        data = self._processor().filter_post(data)

        block, invalid = self._gen_validate(data)

        self.g_context['block'] = block

        # update our state var for later update_success calls
        self._last_valid = 'render'

        # run our form validators at the end
        if not block:
            self.success_header_generate()
        else:
            self.error_header_generate(invalid, block)
        return (not block), self.render()

    def validator(self):
        """ This is provided as a convenience method for Validation logic that
        is one-off, and only intended for a single form. Simply override this
        function and access any of your Nodes and their data via the self. This
        method will be called after all other Validators are run. """
        pass

    def update_success(self, update_dict, raw=False):
        """ This method serves as an easy way to update your success attributes
        that are passed to the start Node rendering context, or passed back in
        JSON. It automatically recalls whether the last validation call was to
        json_validate or validate_render and modifys the correct dictionary
        accordingly.

        :param update_dict: The dictionary of values to update/add.
        :type data: dictionary

        :param raw: Whether you would like a pre-compiled JSON
            string returned, or the raw dictionary.
        :type raw: bool

        :return: Return value is either the new JSON string (or raw dict if
            requested) if json_validate was your last validation call, or a
            re-render of the form with updated error messages if validate_render
            was your last call.
        """

        if self._last_valid == 'render':
            try:
                self.start.errors[-1].update(update_dict)
            except IndexError:
                raise IndexError("Error updating your error dictionary for the "
                               "start Node. There were no errors to modify.")
            except AttributeError:
                raise AttributeError("This method is designed to update an "
                                     "error dictionary, yet your errors are "
                                     "not dictionaries")

            return self.render()

        # We're going to default to json render
        else:
            # Modify our last json dict
            try:
                self._last_raw_json['success_blob'].update(update_dict)
            except KeyError:
                raise KeyError("Either your json_validate method has not been "
                               "run yet, or your success_header_generate does"
                               " not produce output")

            # Continue the raw semantic...
            if raw:
                return self._last_raw_json
            else:
                return json.dumps(self._last_raw_json)
