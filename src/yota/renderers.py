import os

class Renderer(object):
    """ Renderers are invoked when a render method of a :class:`Form` is
    executed. Currently these include :meth:`Form.render` and
    :meth:`Form.validate_render`. Renderers were designed mainly to allow the
    interchange of template engines and context gathering semantics. As of now
    only the JinjaRenderer is availible, unless you want to write one :).
    """
    pass

class JinjaRenderer(Renderer):
    from jinja2 import Environment, FileSystemLoader
    # automatically populate our search path with the default templates
    search_path = [os.path.dirname(os.path.realpath(__file__)) +
            "/templates/jinja/"]
    _env = None
    suffix = ".html"

    @property
    def env(self):
        """ Simple lazy loaders """
        if not self._env:
            self._env = JinjaRenderer.Environment(loader=JinjaRenderer.FileSystemLoader(JinjaRenderer.search_path))
        return self._env

    def render(self, nodes, g_context):
        buildup = ""
        for node in nodes:
            template = self.env.get_template(node.template + self.suffix)
            buildup += template.render(node.get_context(g_context))
        return buildup
