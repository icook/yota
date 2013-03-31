from collections import OrderedDict
from yota.exceptions import ValidatorNotCallable
from yota.renderers import JinjaRenderer
from yota.processors import FlaskPostProcessor
from yota.nodes import Node
from yota.validators import Check
import json
import copy

class OrderedDictMeta(type):
    def __init__(mcs, name, bases, dict):
        """ Basically do a whole lot of convoluted work to preserve
        order of our attributes as they were entered
        """
        t = {}
        mcs._validation_list = []
        for name, value in dict.items():
            if isinstance(value, Node):
                value._attr_name = name
                t[value._create_counter] = value
                if hasattr(value, 'validators'):
                    if not isinstance(value.validator, tuple) and \
                       not isinstance(value.validator, list):
                        value.validators = (value.validators,)
                    for validator in list(value.validators):
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
    __metaclass__ = OrderedDictMeta

    g_context = {}
    context = {}
    _renderer = JinjaRenderer
    _processor = FlaskPostProcessor
    enable_error_header = True
    start_template = 'form_open.html'
    close_template = 'form_close.html'

    def __new__(cls, **kwargs):
        # We want our created Form to have a copy of the origninal
        # form list so that dynamic additions to the list do not
        # effect all Form instances
        c = super(Form, cls).__new__(cls, **kwargs)
        c._node_list = copy.deepcopy(cls._node_list)
        for n in c._node_list:
            setattr(c, n._attr_name, n)
        c._validation_list = copy.deepcopy(cls._validation_list)
        for n in c._validation_list:
            if n._attr_name:
                setattr(c, n._attr_name, n)
        return c

    def __init__(self, name=None, **kwargs):
        # set a default for our name to the class name
        self.name = name if name else self.__class__.__name__

        # since our default id is based off of the parent id
        # we can pass it in here
        for n in self._node_list:
            n.set_identifiers(self.name)

        # Add our open and close form to the end of the tmp lst
        n = self._node_list  # alias node list
        if not hasattr(self, 'begin'):
            self.insert(0, Node(template=self.start_template,
                         _attr_name='begin',
                         **self.context))
        else:
            self.insert(0, self.begin)

        if not hasattr(self, 'close'):
            self.insert(-1, Node(template=self.close_template,
                       _attr_name='close',
                       **self.context))
        else:
            self.insert(-1, self.close)


        # passes everything to our rendering context and updates params
        self.context.update(kwargs)

    def render(self):
        """ Runs the renderer to actually parse templates of nodes
        and generate the form HTML. Also handles adding the begin
        and end template nodes from the parent form. """

        return self._renderer().render(self._node_list, self.g_context)

    def insert(self, position, new_node_list):
        # check to allow passing in just a node
        if isinstance(new_node_list, Node):
            new_node_list = (new_node_list,)

        for i, new_node in enumerate(new_node_list):
            if position == -1:
                self._node_list.append(new_node);
            else:
                self._node_list.insert(position + i, new_node);
            setattr(self, new_node._attr_name, new_node)
            new_node.set_identifiers(self.name)

    def insert_after(self, prev_attr_name, new_node_list):
        """ Runs through the internal node structure attempting to find
        prev_attr_name and inserts the passed node after it. If the
        prev_attr_name cannot be found it will be inserted at the end """

        # check to allow passing in just a node
        if isinstance(new_node_list, Node):
            new_node_list = (new_node_list,)

        # Loop through our list of nodes to find where to insert
        for index, node in enumerate(self._node_list):
            # found!
            if node._attr_name == prev_attr_name:
                for i, new_node in enumerate(new_node_list):
                    self._node_list.insert(index + i + 1, new_node);
                    setattr(self, new_node._attr_name, new_node)
                    new_node.set_identifiers(self.name)
                break
        else:
            # failover append if not found
            for new_node in new_node_list:
                self._node_list.append(new_node)

    def get_by_attr(self, name):
        # Simple accessor wrapper for looking up a node by _attr_name
        try:
            attr = getattr(self, name)
        except:
            return None
        if isinstance(attr, Node):
            return attr
        return None

    def error_header_generate(self, errors):
        """ This method is automatically called when any validators on the
        form fail to pass (unless the validator passes block: False). The
        method should generate a dictionary that will be passed to your
        error renderer, whether that be javascript callbacks or re-rendering
        the form with error info in the rendering context.

        @param errors: This will be a dictionary of all other nodes that have
        errors. Key values are the id of the node while the value is a dict
        of what the validator is passing back.
        """

        return {'message': 'Please resolve the errors below to continue.'}

    def process_validation(self, vdict):
        return vdict

    def _gen_validate(self, data):
        # Allows user to set a modular processor on incoming data
        data = self._processor().filter_post(data)

        for n in self._validation_list:
            print id(n.args)

        # loop over our nodes
        for n in self._validation_list:
            print n
            # try to iterate over their validators
            n.resolve_attr_names(data, self)
            try:
                r = n.validate()
            except TypeError as e:
                raise ValidatorNotCallable("Validators provided must be callable, type '{}' instead.".format(type(n.validator)))
            if r:
                yield (n.target, r)


    def json_validate(self, data):
        """ Runs all the accumulated validators on the data passed and returns the
        result of each failed validation to the target node. Given the data from
        your post call it is run through a post- processor and then validated
        with appropriate node modules """

        # Allows user to set a modular processor on incoming data
        data = self._processor().filter_post(data)

        errors = {}
        block = False
        # loop over our nodes
        for target_node, validation_result in self._gen_validate(data):
            # block by default, unless specified
            block = validation_result.get('block', True)
            # run filter on our validation result
            errors[target_node.id] = self.process_validation(validation_result)

        # if needed we should run our all form message generator and return
        # json encoded error message
        if len(errors) > 0:
            if self.enable_error_header:
                errors['begin'] = self.error_header_generate(errors)
            return json.dumps({'notices': errors, 'success': not block})
        else:
            return json.dumps({'success': not block})

    def validate_render(self, data):
        # Allows user to set a modular processor on incoming data
        data = self._processor().filter_post(data)


        errors = {}
        block = False
        # loop over our nodes
        for target_node, validation_result in self._gen_validate(data):
            # block by default, unless specified
            block = validation_result.get('block', True)
            # run filter on our validation result
            errors[target_node.id] = self.process_validation(validation_result)
            target_node.error = validation_result

        # run our form validators at the end
        if len(errors) > 0:
            if self.enable_error_header:
                self.begin.error = self.error_header_generate(errors)

        return self.render()

