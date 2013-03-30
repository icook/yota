from collections import OrderedDict
from yota.exceptions import ValidatorNotCallable
from yota.renderers import JinjaRenderer
from yota.processors import FlaskPostProcessor
from yota.nodes import Node
import json
import copy

class OrderedDictMeta(type):
    def __init__(mcs, name, bases, dict):
        """ Basically do a whole lot of convoluted work to preserve
        order of our attributes as they were entered
        """
        t = {}
        for name, value in dict.items():
            if isinstance(value, Node):
                value._attr_name = name
                t[value._create_counter] = value
                #delattr(mcs, name)  # Remove the node attr
        mcs._node_list = []
        mcs._node_store = {}
        for i, value in sorted(t.items()):
            # keeps track of the order of items
            mcs._node_list.append(value)

class Form(object):
    __metaclass__ = OrderedDictMeta

    g_context = {}
    context = {}
    _renderer = JinjaRenderer
    _processor = FlaskPostProcessor
    start_template = 'form_open.html'
    close_template = 'form_close.html'

    def __new__(cls, **kwargs):
        # We want our created Form to have a copy of the origninal
        # form list so that dynamic additions to the list do not
        # effect all Form instances
        c = super(Form, cls).__new__(cls, **kwargs)
        c._node_list = copy.deepcopy(cls._node_list)
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
        if not hasattr(self, 'start'):
            begin = Node(template=self.start_template,
                         _attr_name='begin',
                         **self.context)
        else:
            begin = self.begin
        if not hasattr(self, 'close'):
            end = Node(template=self.close_template,
                       _attr_name='close',
                       **self.context)
        else:
            end = self.close

        n.insert(0, begin)
        n.append(end)

        # passes everything to our rendering context and updates params
        self.context.update(kwargs)

    def render(self):
        """ Runs the renderer to actually parse templates of nodes
        and generate the form HTML. Also handles adding the begin
        and end template nodes from the parent form. """

        return self._renderer().render(self._node_list, self.g_context)

    def insert_after(self, prev_attr_name, new_node_list):
        """ Runs through the internal node structure attempting to find
        prev_attr_name and inserts the passed node after it. If the
        prev_attr_name cannot be found it will be inserted at the end """

        # check to allow passing in just a node
        if isinstance(new_node_list, Node):
            new_node_list = tuple(new_node_list)

        for new_node in new_node_list:
            for index, node in enumerate(self._node_list):
                if node._attr_name == prev_attr_name:
                    self._node_list.insert(index + 1, new_node);
                    new_node.set_identifiers(self.name)
                    break
            else:
                # failover append if not found
                self._node_list.append(new_new)


    def validate(self, data):
        """ Given the data from your post call it is run through a post-
        processor and then validated with appropriate node modules """

        # Allows user to set a modular processor on incoming data
        data = _processor().filter_post(data)
        errors = {}
        # loop over our nodes
        for n in self._node_list:
            # try to iterate over their validators
            for val in list(n.validators):
                try:
                    r = val(n)
                except TypeError:
                    raise ValidatorNotCallable("Validators provided must be callable, type '{}' instead.".format(type(val)))
                # if our function returned an error
                if r:
                    errors[n.id] = list(r)

        # run our form validators at the end

        return errors

    def json_validate(self):
        return json.dumps(self.validate())




