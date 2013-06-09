from yota.exceptions import InvalidContextException, DataAccessException


class Node(object):
    """ Nodes are holders of context for rendering and displaying validating
    for a portion of your :class:`Form`. This default base Node is designed to
    provide a template along with specific context information to a templating
    engine such as Jinja2. For validation a Node acts as an information source
    or an error sink. Essentially Nodes can be used to source data for use in a
    :class:`Check`, and they can then be delivered some sort of validation
    error via a the internal :attr:`errors` attribute.

    .. note:: By default all keyword attributes passed to a Node's init
        function are passed onto the rendering context. To override this,
        use the
        :attr:`Node._ignores` attribute.

    :param _attr_name: This is how the Node is identified in the Form. If
        populated automatically if the Node is defined in an a Form class
        definition, however if the Node is added dynamically it will need to be
        defined before adding it to the Form.
    :type _attr_name: string

    :param _ignores: A List of attribute names to explicity not include in the
        rendering context. Mostly a niceity for keeping the rendering context
        clutter free.
    :type _ignores: list

    :param _requires: A List of attributes that will be required at
        render time. An exception will be thrown if these attributes are not
        present.  Useful for things like lists that require certain data to
        render properly.
    :type _requires: list

    :param template: String name of the template to be parsed upon
        rendering.  This is passed into the `Form._renderer` so it needs to
        be whatever that is designed to accept. Jinja2 is looking for a
        filename like 'node' that occurs in it's search path.
    :type template: string

    :param validator: An optional attribute that specifies a
        :class:`Check` object to be associated with the Node. This is
        automatically extracted at parse time and cannot be manipulated
        after Node insertion.
    :type validator: callable

    The default Node init method accepts any keyword arguments and adds them to
    the Node's rendering context.

    """

    _create_counter = 0
    """ Allows tracking the order of Node creation """

    def __init__(self,
                 template=None,
                 validator=None,
                 label=True,
                 _requires=None,
                 _ignores=None,
                 _attr_name=None,
                 **kwargs):

        # Allow _ignores and _requires to be overwritten at the instance level,
        # and also have a default
        if _ignores:
            self.ignores = _ignores
        elif not hasattr(self, '_ignores'):
            self._ignores = ['template', 'validator']

        if _requires:
            self._requires = _requires
        elif not hasattr(self, '_requires'):
            self._requires = []

        if not hasattr(self, 'validator'):
            self.validator = validator

        if template:
            self.template = template
        self._attr_name = _attr_name
        self.label = label

        # Allows the parent form to keep track of attribute order
        self._create_counter = Node._create_counter
        Node._create_counter += 1

        # A placeholder for validation process
        self.errors = []
        self.data = ''

        # passes everything to our rendering context and updates params
        self.__dict__.update(kwargs)

    def add_error(self, error):
        """ This method serves mostly as a wrapper alowing for different error
        ordering semantics, or possibly error post-processing. Errors from
        validation methods should be added in this way allowing them to be
        caught. More information about what gets passed in in the
        :doc:`Validators` section. """
        self.errors.append(error)

    def set_identifiers(self, parent_name):
        """ This function gets called by the parent `Form` when it is
        initialized or inserted. It is designed to set various unique
        identifiers. By default it generates an id for the Node that is
        {parent_name}_{_attr_id}, a title for the Node that is the _attr_name
        capitalized, and a name for the element that is just the _attr_name.
        All of these attributes are then passed onto the rendering context of
        the Node by default. By default all of these attributes will yield to
        attributes passed into the __init__ method.

        :param parent_name: The name of the parent form. Useful in ensuring
            unique identifiers on your element names.
        :type parent_name: string
        """

        # Set some good defaults based on attribute name and parent name,
        # but always allow the user to override the values at the init level
        if not hasattr(self, 'id'):
            self.id = "{0}_{1}".format(parent_name, self._attr_name)
        if not hasattr(self, 'name'):
            self.name = self._attr_name
        if not hasattr(self, 'title'):
            self.title = self._attr_name.capitalize().replace('_', ' ')

    def resolve_data(self, data):
        """ This method is called when resolving the data from a form
        submission and linking it to a specific Node. The return value of this
        function is passed directly to the Validators data portion for your
        node. By default this will try and lookup data from the submission
        using the name attribute. """
        try:
            self.data = data[self.name]
        except KeyError:
            raise DataAccessException

    def get_context(self, g_context):
        """ Builds our rendering context for the Node at render time. By
        default all attributes of the Node are added to the global namespace
        and the global rendering context is passed in under the variable 'g'.
        This function is designed to be overridden for customization.  :param
        g_context: The global rendering context passed in from the rendering
        method.  """

        # Dat 2.6 compat, no dict comprehensions :(
        d = {}
        for key in dir(self):
            if not key.startswith("_") and key not in self._ignores:
                d[key] = getattr(self, key)

        # check to make sure all required attributes are present
        for r in self._requires:
            if r not in d:
                raise InvalidContextException(
                    "Missing required context value '{0}'".format(r))
        d['g'] = g_context
        return d


class BaseNode(Node):
    """ This base Node supplies the name of the base rendering template the
    is used for standard form elements. This base template provides error
    divs and the horizontal form layout for Bootstrap.
    """
    base = "horiz.html"
    css_class = ''
    css_style = ''


class ListNode(BaseNode):
    """ Node for providing a basic drop down list. Requires an attribute that
     is a list of tuples providing the key and value for the dropdown list
     items.
    """
    template = 'list'
    _requires = ['items']


class GroupedInputsNode(BaseNode):
    """ Node for providing a group of input elements, designed with radio
     elements in mind. Requires an attribute that is a list of tuples
     providing the value for the items and description for labels.
    """
    template = 'grouped_elements'
    type = 'radio'
    _requires = ['buttons']


class ButtonNode(BaseNode):
    """ Creates a simple button in your form.
    """
    template = 'button'


class EntryNode(BaseNode):
    template = 'entry'


class TextareaNode(BaseNode):
    """ A node with a basic textarea template with defaults provided  """
    template = 'textarea'
    rows = '5'
    columns = '10'


class SubmitNode(BaseNode):
    template = 'submit'


class LeaderNode(Node):
    """ A Node that simply removes the title attribute from the Node rendering
    context. Intended for use in the start and end Nodes. """

    form_class = "form-horizontal"

    def set_identifiers(self, parent_name):
        # set our start node's id to actually be the name of the form
        if not hasattr(self, 'id'):
            self.id = parent_name

        super(LeaderNode, self).set_identifiers(parent_name)
        delattr(self, 'title')
