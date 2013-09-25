from jinja2 import Environment, FileSystemLoader
import os


class JinjaRenderer(object):

    templ_type = 'bs2'
    """
    Allows you to switch the default template set being used. Default templates
    for JinjaRenderer are stored in /templates/jinja/{templ_type}/. Below code
    being run before your render method will change templates to Bootstrap 3.0.
    This is usually run when setting up web framework configs to take effect
    globally. See the flask example for more information.

    .. code-block:: python

        import os
        from yota.renderers import JinjaRenderer

        JinjaRenderer.templ_type = "bs3"

    .. note:: In order to display errors correctly the :attr:`Form.type_class_map`
        must be overriden so alert-error can be changed to alert-danger for
        Bootstrap 3.

    """
    search_path = []
    """
    The list of paths that Jinja will look for templates in. It scans
    sequentially, so inserting custom template paths at the beginning is an
    easy way to override default templates without touching Yota. The default
    path is appended to the end of this list the first time render is called.
    """
    _env = None
    """
    The Jinja rendering enviroment. This is lazily loaded.
    """

    suffix = ".html"
    """ The default template suffix """

    @property
    def env(self):
        """ Simple lazy loader for the Jinja2 enviroment """
        if not self._env:
            path = os.path.dirname(os.path.realpath(__file__)) \
                               + "/templates/" + self.templ_type + "/jinja/"
            if path not in self.search_path:
                self.search_path.append(path)
            loader = FileSystemLoader(JinjaRenderer.search_path)
            self._env = Environment(loader=loader)
        return self._env

    def render(self, nodes, g_context):
        """ Loop over each Node passed in by nodes and render it into a big
        blob of a string. Passes g_context to each nodes
        :meth:`Node.get_context`. """
        buildup = ""
        for node in nodes:
            template = self.env.get_template(node.template + self.suffix)
            buildup += template.render(node.get_context(g_context))
        return buildup
