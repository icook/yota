from collections import OrderedDict
from yota import Renderer

class Node(object):
    """ I'm a simple example node
    """
    _create_counter = 0
    template = None

    def __init__(self):
        self._create_counter = Node._create_counter
        Node._create_counter += 1

    def get_context(self, g_context):
        """ Builds our rendering context that includes everything that's not private
        and merges in our global context. Called by our renderer at render time
        """
        d = {i: j for i, j in self.__dict__.items() if not j.startswith("_") }
        d.update(g_context)
        return d

class ListNode(Node):
    template = 'list'

class ButtonNode(Node):
    template = 'button'

class OrderedDictMeta(type):
    def __new__(mcs, name, bases, dict):
        """ Basically do a whole lot of convoluted work to preserve
        order of our attributes as they were entered
        """
        t = {}
        for name, value in dict.items():
            if isinstance(value, Node):
                value.name = name
                t[value._create_counter] = value
        mcs._nodes = OrderedDict()
        for i, value in t.items():
            mcs._nodes[value.name] = value
        return type.__new__(mcs, name, bases, dict)


class Form(object):
    __metaclass__ = OrderedDictMeta

    g_context = []
    context = []
    renderer = Renderer
    template = 'form'
    name = ''


    def __setattr__(self, key, value):
        print "{} {}".format(key, value)

    def render(self):
        return self.renderer.render(self._nodes, self.g_context, self.context, self.template)


class SimpleForm(Form):
    test = ButtonNode()
    that = ButtonNode()
    whoo = ListNode()
