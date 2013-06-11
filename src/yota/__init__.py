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

    def __init__(self,
                 name=None,
                 auto_start_close=True,
                 start_template='form_open',
                 close_template='form_close',
                 g_context=None,
                 context=None,
                 start=None,
                 close=None,
                 **kwargs):
        self.auto_start_close = auto_start_close
        self.start_template = start_template
        self.close_template = close_template
        self.g_context = g_context if g_context else {}
        self.context = context if context else {}

        # set a default for our name to the class name
        self.name = name if name else self.__class__.__name__

        # passes everything to our rendering context and updates params
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
            return None
        if isinstance(attr, Node):
            return attr
        return None

    def error_header_generate(self, errors, block):
        """ This method is called when any validators on the form fail
        to pass.  The method should generate a dictionary that will be
        passed to your error renderer, whether that be javascript
        callbacks or re-rendering the form with error info in the
        rendering context.

        :param errors: This will be a list of all other Nodes that have errors.
        :param block: Whether or not the form submission will be blocked.
        :type block: boolean

        By default this function does nothing, but a common method of
        implementing it may be as follows:
        .. code-block:: python

            self.start.add_error(
                {'message': 'Please resolve the errors below to continue.'})

        This will provide a simple error message to your start Node.
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

        # reset all error lists and data
        for node in self._node_list:
            node.errors = []
            node.data = ''

        # Allows user to set a modular processor on incoming data
        data = self._processor().filter_post(data)

        # assume to be not blocking
        block = False
        # loop over our checks and run our validators
        for check in self._validation_list:
            # try to iterate over their validators
            try:
                check.resolve_attr_names(data, self)
            except DataAccessException as e:
                # ignore the exception if we're in piecewise mode
                if not piecewise:
                    raise e
                else:
                    # make sure no success until all validators can run
                    block = True
                    continue
            try:
                # Run our validator
                check.validate()
            except TypeError as e:
                raise NotCallableException(
                    "Validators provided must be callable, type '{0}'" +
                    "instead. Caused by {1}".format(type(check.validator), e))

        # a list to hold Nodes that actually have errors
        error_node_list = []
        for node in self._node_list:
            # slightly confusing way of setting our block = True by
            # default
            if node.errors:
                error_node_list.append(node)
            else:
                # if the data field is blank, try and populate it
                if node.data == '':
                    try:
                        node.resolve_data(data)
                    except DataAccessException:
                        pass
                continue

            if not block:  # no sense in checking if already blocking
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
        # pass our data into the global rendering context for filling in info
        self.g_context['data'] = data

        errors = {}
        block, invalid = self._gen_validate(data, piecewise=piecewise)
        # auto-disable if this is not the submit action and it's a piecewise to
        # prevent auto-submission
        if data.get('submit_action', 'false') != 'true' and piecewise:
            block = True

        # loop over our nodes and insert information for the JS callbacks
        for node in invalid:
            errors[node._attr_name] = {'identifiers': node.json_identifiers(),
                                       'errors': node.errors}

        # if needed we should run our all form message generator and return
        # json encoded error message
        retval = {'success': not block}
        if len(errors) > 0:
            errors['start'] = {'identifiers': self.start.json_identifiers(),
                               'errors': self.error_header_generate(errors, block)}
        retval['errors'] = errors
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
