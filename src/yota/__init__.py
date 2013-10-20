from yota.renderers import JinjaRenderer
from yota.processors import FlaskPostProcessor
from yota.nodes import Leader, Node, Blueprint
from yota.validators import Check, Listener
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
        mcs._event_lists = {}
        for name, attribute in dct.items():
            # These aren't ordered Nodes, ignore them
            if name is 'start' or name is 'close':
                try:
                    attribute._attr_name = name
                    continue
                except AttributeError:
                    raise AttributeError("start/close attribute is special and"
                        "should specify a Node to begin your form. Got type {0}"
                        "instead".format(type(name)))
            if isinstance(attribute, Node):
                attribute._attr_name = name
                nodes[attribute._create_counter] = attribute
                delattr(mcs, name)
            elif isinstance(attribute, Check):
                # if we've found a validation check
                attribute._attr_name = name
                mcs._validation_list.append(attribute)
                delattr(mcs, name)
            elif isinstance(attribute, Listener):
                # if we've found a validation check
                attribute._attr_name = name
                if attribute.type not in mcs._event_lists:
                    mcs._event_lists[attribute.type] = []
                mcs._event_lists[attribute.type].append(attribute)
                delattr(mcs, name)
            else:
                # just assume that this is some kind of blueprint with
                # ducktyping
                try:
                    for node in attribute._node_list:
                        nodes[node._create_counter] = node
                except AttributeError:
                    pass

                # merge in our events
                try:
                    for key, lst in attribute._event_lists.items():
                        if key in mcs._event_lists:
                            mcs._event_lists[key].extend(lst)
                        else:
                            mcs._event_lists[key] = lst
                except AttributeError:
                    pass

                # and validation
                try:
                    mcs._validation_list.extend(attribute._validation_list)
                except AttributeError:
                    pass

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
    _success_data = None
    """ Hold information that will be serialized into success return values
    for render_json """
    _submit_action = False
    """ Tracks whether you're submitting the form, or just validating it for
    later json serialization """

    """ This declares which backend is used when storing semi-persistent
    information such as CSRF tokens and CAPTCHA solutions. """
    pysistor_backend = None
    """ This defines an adapter object that will be made availible to the
    Pysistor backend for use in storing the data. For instance, access to
    sessions frequently requires access to the request object and an adapter
    can carry that information. More information on this behaviour can be
    gotten in the pysistor documentation """
    pysistor_adapter = None

    name = None
    context = {}
    g_context = {}
    title = None
    auto_start_close = True
    start_template = 'form_open'
    close_template = 'form_close'
    render_success = False
    render_error = False
    type_class_map = {'error': 'alert alert-error',
                      'info': 'alert alert-info',
                      'success': 'alert alert-success',
                      'warn': 'alert alert-warn'}
    """ A mapping of error types to their respective class values. Used to
    render messages to the user from validation. Changing it to render messages
    differently could be performed as follows:

    .. code-block:: python

        class MyForm(yota.Form):
            first = EntryNode(title='First name', validators=Check(MinLengthValidator(5)))
            last = EntryNode(title='Last name', validators=MinLengthValidator(5)

            # Override the default type_class_map with our own
            type_class_map = {'error': 'alert alert-error my-special-class', # Add an additional class
                            'info': 'alert alert-info',
                            'success': 'alert alert-success',
                            'warn': 'alert alert-warn'}
    """


    def __init__(self, **kwargs):
        # A bit of a hack to copy all our class attributes
        for class_attr in dir(self):
            if class_attr in kwargs:
                continue
            att = getattr(self, class_attr)
            # We want to copy all the nodes as well as the list, this is a
            # succinct way to do it
            if class_attr in ['_node_list', '_validation_list', '_event_lists']:
                setattr(self, class_attr, copy.deepcopy(att))
            # Private attributes are internal stuff..
            elif not class_attr.startswith('__'):
                # don't try to copy functions, it doesn't go well
                if not callable(att):
                    new = copy.copy(att)
                    setattr(self, class_attr, new)
                    self.context[class_attr] = new

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
                self.insert(0, Leader(template=self.start_template,
                                        _attr_name='start',
                                        **self.context))
        if hasattr(self, 'close'):
            self._node_list.append(self.close)
        else:
            if self.auto_start_close:
                self.insert(-1, Leader(template=self.close_template,
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
        setattr(node, "_parent_form", self)

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

    def _process_errors(self):
        for node in self._node_list:
            # process the node errors and inject special values
            for error in node.errors:
                # Try and retrieve the class values for the result type
                # and send along the required render value
                try:
                    error['_type_class'] = self.type_class_map[error['type']]
                except KeyError:
                    error['_type_class'] = self.type_class_map['error']

    def is_piecewise(self):
        return bool('piecewise' in self.g_context and self.g_context['piecewise'])

    def add_listener(self, listener):
        """ Attaches a :class:`Listener` to an event type. These Listener will
        be executed when trigger event is called. """
        if type not in self._event_lists:
            self._event_lists[listener.type] = []
        self._event_lists[listener.type].append(listener)

    def trigger_event(self, type):
        """ Runs all the associated :class:`Listener`'s for a specific event
        type. """
        try:
            for event in self._event_lists[type]:
                event.resolve_attr_names(self)
                event()
        except KeyError:
            pass
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

    def resolve_all(self, data):
        """ This is a utility method that runs resolve_data on all nodes with
        the provided data dictionary. """
        for node in self._node_list:
            node.resolve_data(data)

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

    def success_json_generate(self):
        """ Please see the documentation for :meth:`Form.error_header_generate`
        as it covers this function as well as itself. """
        pass

    def error_header_generate(self, errors):
        """ This function is generally used to generate a header on the start
        Node automatically when there is an error in validation. For instance,
        you might want to say "Please fix the errors below" or something
        similar. While it could actually be used for anything post-validation
        failure, it is better practice to create a listener that subscribes to
        "validation_failure" event, as this function is called at the same time.

        :param errors: This will be a list of all other Nodes that have errors,
            with the idea that you might want to list the errors that occurred.
        :type errors: list

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

    def validate_json(self, data, piecewise="auto", raw=False):
        """ The same as :meth:`Form.validate_render` except the errors
        are loaded into a JSON string to be passed back as a query
        result. This output is designed to be used by the Yota
        Javascript library.

        :param piecewise: This parameter is deprecated. Piecewise is
            automatically detected from g_context.

        :param raw: If set to True then the second return parameter will be a
            Python dictionary instead of a JSON string
        :type raw: boolean

        :return: A boolean whether or not the form submission is valid and the
            json string (or raw dictionary) to pass back to the javascript side.
            The boolean is an anding of submission (whether the submit button was
            actually pressed) and the block parameter (whether or not any blocking
            validators passed)
        """

        success, invalid = self.validate(data, internal=True, piecewise=piecewise)
        return success, self.render_json(invalid=invalid, success=success, raw=raw)

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
        success = self.validate(data)
        return success, self.render()

    def render_json(self, invalid=None, success=None, raw=False):
        """ This function takes the state that is stored internally and
        serializes it into a form that the yota JS library is designed to
        recieve. """

        # If a list of invalid nodes wasn't included, build it. This is
        # because json_validate can pass this function the list, and success
        # info from validate directly if they aren't called separately
        block = False
        if not invalid or not success:
            invalid = []
            for node in self._node_list:
                if node.errors:
                    invalid.append(node)

                # slightly confusing way of setting our block = True by
                # default
                for error in node.errors:
                    block |= error.get('block', True)

            # Make sure they have run validate
            if self._submit_action and not block:
                success = True
            else:
                success = False

        errors = {}

        # convert node errors into a format for the JS callbacks
        for node in invalid:
            errors[node._attr_name] = {'identifiers': node.json_identifiers(),
                                       'errors': node.errors}

        retval = {'success': success}

        # add our success header generate results if needed, else success_data
        if success:
            if not self._success_data:
                blob = self.success_json_generate()
                if blob:
                    retval['success_blob'] = blob
            else:
                retval['success_blob'] = self._success_data

            if hasattr(self, 'start'):
                retval['success_ids'] = self.start.json_identifiers()


        retval['errors'] = errors

        # process the errors before we serialize
        self._process_errors()

        # Return our raw dictionary if requested, otherwise serialize for
        # convenience...
        if raw:
            return retval
        else:
            return json.dumps(retval)

    def render(self):
        """ Runs the renderer to parse templates of nodes and generate the form
        HTML.

        :returns: A string containing the generated output.
        """
        # process the errors before we render
        self._process_errors()

        return self._renderer().render(self._node_list, self.g_context)

    def validate(self, data, piecewise="auto", internal=False, resolver=None):
        """ Runs all the validators associated with the :class:`Form`.

        :return: Whether validation was successful
        """
        piecewise = piecewise if piecewise != "auto" else self.is_piecewise()

        # Allows user to set a modular processor on incoming data
        data = self._processor().filter_post(data)

        # reset all error lists and data, then re-resolve with the new data.
        # also parse nodes for shorthand validators at this time
        for node in self._node_list:
            node.errors = []
            node.data = ''
            node.resolve_data(data)
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
            check.resolve_attr_names(self)
            # Run the check if we're not in piecewise mode, or if the check
            # tells us all relevant form elements have been visited
            if piecewise is False or check.node_visited(visited):
                check()
            else:
                # If even a single check can't be run, we need to block
                block = True

        # Run the one off validation method
        self.validator()

        # a list to hold Nodes that actually have errors. while this list isn't
        # used in this function, it's cheap to generate and saves a loop if
        # serialization is run at the same time as validation
        invalid = []
        for node in self._node_list:
            if node.errors:
                invalid.append(node)

            # slightly confusing way of setting our block = True by
            # default
            for error in node.errors:
                block |= error.get('block', True)

        # If it's blocking right now then there was an error, so generate
        # the error header
        header_err = self.error_header_generate(invalid)
        if header_err:
            self.start.add_error(header_err)

        # Run our validation trigger events. At this point block represents just
        # the validation
        if block:
            self.trigger_event("validate_failure")
        else:
            self.trigger_event("validate_success")

        # Block if they aren't actually submitting the form. Also, flag as a
        # non-submit for later serialization
        if data.get('submit_action', 'false') != 'true' and piecewise:
            self._submit_action = False
            block = True
        else:
            self._submit_action = True

        if internal:
            return (not block), invalid
        else:
            return not block
    _gen_validate = validate

    def validator(self):
        """ This is provided as a convenience method for Validation logic that
        is one-off, and only intended for a single form. Simply override this
        function and access any of your Nodes and their data via the self
        attribute. This method will be called after all other Checks are
        run. """
        pass

    def set_json_success(self, **kwargs):
        """ As opposed to using generate_json_success to pass information
        to the js success function you can use add_success in your view code. """

        self._success_data = kwargs
