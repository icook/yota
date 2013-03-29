from exceptions import InvalidContext

class Node(object):
    """ Base node for all other nodes
    """
    _create_counter = 0
    # a list of attributes that must be provided for rendering to proceed
    _requires = []
    # a list of attributes to not put in the rendering context
    _ignores = ['template', 'validator']

    template = None
    validator = None
    #name = attribute set in the parent form or can be passed to init

    def __init__(self, **kwargs):
        # Allows the parent form to keep track of attribute order
        self._create_counter = Node._create_counter
        Node._create_counter += 1

        # passes everything to our rendering context and updates params
        self.__dict__.update(kwargs)


    def set_id(self, parent_name):
        """ Function that gets called by the parent Form to set the text
        id of the form node. Intended for use in the id field for rendering
        """
        self.id = "{}_{}".format(parent_name, self.name)

    def get_context(self, g_context):
        """ Builds our rendering context that includes everything that's not private
        and merges in our global context. Called by our renderer at render time
        """
        d = {i: j for i, j in self.__dict__.items() if not i.startswith("_") and i not in _ignores }
        # check to make sure all required attributes are present
        for r in self._requires:
            if r not in d:
                raise InvalidContext("Missing required context value '{}'".format(r))
        d.update(g_context)
        return d

class ListNode(Node):
    template = 'list.html'

class ButtonNode(Node):
    template = 'button.html'

