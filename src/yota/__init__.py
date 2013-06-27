from yota.exceptions import DataAccessException, NotCallableException
from yota.renderers import JinjaRenderer
from yota.processors import FlaskPostProcessor
from yota.nodes import LeaderNode, Node
from yota.validators import Check
import json
import copy

class TrackingMeta(type):
    def __init__(mcs, name, bases, dict):
        """ Process all of the attributes in the `Form` (or subclass)
        declaration and place them accordingly. This builds the internal
        _node_list and _validation_list. """

        t = {}
        mcs._validation_list = []
        for name, value in dict.items():
            if isinstance(value, Node):
                value._attr_name = name
                t[value._create_counter] = value
                if hasattr(value, 'validators'):
                    if not isinstance(value.validators, tuple) and \
                       not isinstance(value.validators, list):
                        value.validators = [value.validators, ]
                    for validator in value.validators:
                        # shorthand for adding a validation tuple
                        c = Check(validator, name)
                        mcs._validation_list.append(c)
            elif isinstance(value, Check):
                # if we've found a validation tuple
                value._attr_name = name
                mcs._validation_list.append(value)

        mcs._node_list = []
        for i, value in sorted(t.items()):
            # keeps track of the order of items for actual rendering
            mcs._node_list.append(value)


class Form(object):
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

    def __new__(cls, **kwargs):
        """ We want our created Form to have a copy of the original
        form list so that dynamic additions to the list do not
        effect all Form instances """

        c = super(Form, cls).__new__(cls, **kwargs)
        c._node_list = copy.deepcopy(cls._node_list)
        for n in c._node_list:
            setattr(c, n._attr_name, n)
        c._validation_list = copy.deepcopy(cls._validation_list)
        for n in c._validation_list:
            if n._attr_name:
                setattr(c, n._attr_name, n)
        return c

    def __init__(self,
                 name=None,
                 auto_start_close=None,
                 start_template=None,
                 close_template=None,
                 g_context=None,
                 context=None,
                 start=None,
                 close=None,
                 **kwargs):

        """ Basically, set the instance attribute to one of the following in
        order of preference:
        1. Passed in parameter
        2. Class attribute
        3. Set default """
        def override(value, attr, default):
            if value:
                setattr(self, attr, value)
            elif not hasattr(self, attr):
                setattr(self, attr, default)

        # override semantics
        override(auto_start_close, 'auto_start_close', True)
        override(start_template, 'start_template', 'form_open')
        override(close_template, 'close_template', 'form_close')
        override(g_context, 'g_context', {})
        override(context, 'context', {})

        # set a default for our name to the class name
        self.name = name if name else self.__class__.__name__
        self.context['name'] = self.name  # pass it to start/close

        # pass some special keywords to our context if they're defined as class
        # attributes
        if hasattr(self, 'title'):
            self.context['title'] = self.title
        # passes everything to our rendering context and updates params.
        # Overwrites class attributes
        self.context.update(kwargs)

        # since our default id is based off of the parent id
        # we can pass it in here
        for n in self._node_list:
            n.set_identifiers(self.name)

        # Add our open and close form defaults
        if not start and not hasattr(self, 'start'):
            if self.auto_start_close:
                self.insert(0, LeaderNode(template=self.start_template,
                                        _attr_name='start',
                                        **self.context))
        else:
            # prefer a parameter over a class attr
            ins = start if start else self.start
            if isinstance(ins, Node):
                self.insert(0, ins)
            else:
                raise AttributeError("start attribute is special and should "
                                     "specify a Node to begin your form")

        # do the same for close
        if not close and not hasattr(self, 'close'):
            if self.auto_start_close:
                self.insert(-1, LeaderNode(template=self.close_template,
                                        _attr_name='close',
                                        **self.context))
        else:
            # prefer a parameter over a class attr
            ins = close if close else self.close
            if isinstance(ins, Node):
                self.insert(-1, ins)
            else:  # provide a bit of error notif
                raise AttributeError("close attribute is special and should "
                                     "specify a Node to begin your form")

    def render(self):
        """ Runs the renderer to parse templates of nodes and generate the form
        HTML.

        :returns: A string containing the generated output.
        """

        return self._renderer().render(self._node_list, self.g_context)

    def insert_validator(self, new_validator):
        """ Inserts a validator to the validator list.

        :param validator: The :class:`Check` to be inserted.
        :type validator: Check """

        # check to allow passing in just a node
        if not isinstance(new_validator, Check):
            raise TypeError

        new_validator._attr_name = new_validator.args[0]
        self._validation_list.append(new_validator)
        setattr(self, new_validator._attr_name, str(new_validator.args))


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
            if position == -1:
                self._node_list.append(new_node)
            else:
                self._node_list.insert(position + i, new_node)
            setattr(self, new_node._attr_name, new_node)
            new_node.set_identifiers(self.name)

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
            raise AttributeError('Form attribute {0} couldn\'t be resolved to'
                                 ' a Node'.format(name))
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
        form wide information back to the user for both AJAX validated forms
        and conventionally validated forms, although the mechanisms are
        slightly different. Both functions are run at the end of a successful
        or failed validation call in order to give more information for
        rendering.

        For passing information to AJAX rendering, simply return a dictionary,
        or any python object that can be serialized to JSON. This information
        gets passed back to the JavaScript callbacks of yota_activate in
        slightly different ways. success_header_generate's information will get
        passed to the render_success callback, while error_header_generate will
        get sent as an error to the render_error callback under the context
        start.

        For passing information into a regular rendering context simply access
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

    def json_validate(self, data, piecewise=False):
        """ The same as :meth:`Form.validate_render` except the errors
        are loaded into a JSON string to be passed back as a query
        result. This output is designed to be used by the Yota
        Javascript library.

        :param piecewise: If set to True, the validator will silently
            ignore validator for which it has insufficient information. This
            is designed to be used for the AJAX piecewise validation
            function, although it does not have to be.
        :type piecewise: boolean
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
            retval['final_success'] = 'true'
        return json.dumps(retval)

    def validate(self, data):
        """ Runs all the validators associated with the :class:`Form`.

        :returns: A list of nodes that have errors on failure or True on
            success
        """

        # Allows user to set a modular processor on incoming data
        data = self._processor().filter_post(data)
        block, invalid = self._gen_validate(data)

        if not block:
            return True
        else:
            return invalid

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
        """

        # Allows user to set a modular processor on incoming data
        data = self._processor().filter_post(data)

        block, invalid = self._gen_validate(data)

        self.g_context['block'] = block

        # run our form validators at the end
        if len(invalid) > 0:
            self.error_header_generate(invalid, block)
            return self.render()
        else:
            return True
