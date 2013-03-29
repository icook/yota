from collections import OrderedDict
from yota.exceptions import ValidatorNotCallable
from yota.renderers import JinjaRenderer
from yota.nodes import Node
import json

class OrderedDictMeta(type):
    def __init__(mcs, name, bases, dict):
        """ Basically do a whole lot of convoluted work to preserve
        order of our attributes as they were entered
        """
        t = {}
        for name, value in dict.items():
            if isinstance(value, Node):
                value.name = name
                t[value._create_counter] = value
        mcs._node_list = []
        mcs._node_store = {}
        for i, value in sorted(t.items()):
            # keeps track of the order of items
            mcs._node_list.append(value)
            # allows fast lookup for inserting after names
            mcs._node_store[value.name] = len(mcs._node_list)-1


class Form(object):
    __metaclass__ = OrderedDictMeta

    g_context = {}
    context = {}
    renderer = JinjaRenderer
    start_template = 'form_open.html'
    close_template = 'form_close.html'

    def __init__(self, name=None):
        # set a default for our name to the class name
        self.name = name if name else self.__class__.__name__

        # since our default id is based off of the parent id
        # we can pass it in here
        for n in self._node_list:
            n.set_id(self.name)

    def render(self):
        # Add our open and close form to the node list
        n = self._node_list
        begin = Node(template=self.start_template, **self.context)
        end = Node(template=self.close_template, **self.context)
        n.insert(0, begin)
        n.append(end)

        return self.renderer().render(n, self.g_context)

    def validate(self):
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
        return errors

    def json_validate(self):
        return json.dumps(self.validate())




