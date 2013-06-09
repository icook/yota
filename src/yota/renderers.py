import os


class JinjaRenderer(object):
    from jinja2 import Environment, FileSystemLoader

    # a defualt search path for templates
    search_path = [os.path.dirname(os.path.realpath(__file__))
                   + "/templates/jinja/"]

    # allow lazy loading of the enviroment
    _env = None

    # the default template suffix
    suffix = ".html"

    @property
    def env(self):
        """ Simple lazy loader for the Jinja2 enviroment """
        if not self._env:
            loader = JinjaRenderer.FileSystemLoader(JinjaRenderer.search_path)
            self._env = JinjaRenderer.Environment(loader=loader)
        return self._env

    def render(self, nodes, g_context):
        """ Loop over each Node and render it into a big blob of a string """
        buildup = ""
        for node in nodes:
            template = self.env.get_template(node.template + self.suffix)
            buildup += template.render(node.get_context(g_context))
        return buildup
