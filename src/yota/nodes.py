from yota.exceptions import InvalidContext


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

    def __str__(self):
        return "Node ({})<attr_name: {}, id: {}, _id_: {}>".format(
                self.__class__.__name__,
                self.__dict__.get('_attr_name', None),
                self.__dict__.get('id', None),
                id(self))

    def set_identifiers(self, parent_name):
        """ Function that gets called by the parent Form to set the text
        id of the form node. Intended for use in the id field for rendering
        """
        # Set some good defaults based on attribute name and parent name,
        # but always allow the user to override the values at the init level

        if not hasattr(self, 'id'):
            self.id = "{}_{}".format(parent_name, self._attr_name)
        if not hasattr(self, 'name'):
            self.name = self._attr_name
        if not hasattr(self, 'title'):
            self.title = self._attr_name.capitalize()

    def get_context(self, g_context):
        """ Builds our rendering context that includes everything that's not private
        and merges in our global context. Called by our renderer at render time
        """
        d = {i: getattr(self, i) for i in dir(self) if not i.startswith("_") and i not in self._ignores }
        # check to make sure all required attributes are present
        for r in self._requires:
            if r not in d:
                raise InvalidContext("Missing required context value '{}'".format(r))
        d.update(g_context)
        return d


