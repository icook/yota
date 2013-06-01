from yota.exceptions import InvalidContextException


class Node(object):
    """ Base node for all other nodes. Many Nodes make up a Form. Nodes are
    generally something like a submit button or a username entry field, but in
    practice are simply a template linked together with some metadata and can
    constitute anything. Some non-traditional examples are the opening of the
    form (provided automatically in the `Form` class), perhaps a fieldset tag,
    or a note to display above a particular portion of the `Form`.

    :var _ignores: A list of attributes that won't be passed into the rendering
    context. By default the template and validator attributes are ignored.
    :type _ignore: list

    :var _requires: A list of attributes that are required to render the
    template properly. An exception will be thrown if one of these attributes is
    missing. By default this is empty.
    :type _requires: list

    :var template: String name of the template to be parsed upon rendering. This
    is passed into the `Form._renderer` so it needs to be whatever that is
    designed to accept. Jinja2 is looking for a filename like 'node.html' that
    occurs in it's search path.
    :type template: string

    :var validator: An optional attribute that specifies a `Check` object to be
    associated with the Node.
    :type validator: callable

    The default Node init method accepts any keyword arguments and adds them to
    the Node's rendering context.
    """

    _create_counter = 0
    # a list of attributes that must be provided for rendering to proceed
    _requires = []
    # a list of attributes to not put in the rendering context
    _ignores = ['template', 'validator']

    template = None
    validator = None
    label = True
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
        """ This function gets called by the parent `Form` when it is
        initialized or inserted. It is designed to set verious unique
        identifiers. By default it generates an id for the Node that is
        {parent_name}_{_attr_id}, a title for the Node that is the _attr_name
        capitalized, and a name for the element that is just the _attr_name. All
        of these attributes are then passed onto the rendering context of the
        Node by default.

        :param parent_name: The name of the parent form. Useful in ensuring
        unique identifiers on your element names.
        :type parent_name: string
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
        """ Builds our rendering context for the Node at render time. By default
        all attributes of the Node are added to the global namespace and the
        global rendering context is passed in under the variable 'g'. This
        function is designed to be overridden for customization.  """

        d = {i: getattr(self, i) for i in dir(self) if not i.startswith("_") and i not in self._ignores }
        # check to make sure all required attributes are present
        for r in self._requires:
            if r not in d:
                raise InvalidContextException("Missing required context value '{}'".format(r))
        d['g'] = g_context
        return d

class BaseNode(Node):
    base = "horiz.html"
    css_class = ''
    css_style = ''

class ListNode(BaseNode):
    template = 'list.html'
    _requires = ['items']

class ButtonNode(BaseNode):
    template = 'button.html'

class EntryNode(BaseNode):
    template = 'entry.html'

class TextareaNode(BaseNode):
    template = 'textarea.html'
    rows = '5'
    columns = '10'

class SubmitNode(BaseNode):
    template = 'submit.html'

class LeaderNode(Node):
    """ A Node that simply removes the title attribute from the Node rendering
    context. Intended for use in the start and end Nodes. """

    def set_identifiers(self, parent_name):
        super(LeaderNode, self).set_identifiers(parent_name)
        delattr(self, 'title')
