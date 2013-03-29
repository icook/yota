from jinja2 import Environment, FileSystemLoader
import os

class JinjaRenderer(object):
    # automatically populate our search path with the default templates
    search_path = [os.path.dirname(os.path.realpath(__file__)) + "/templates/"]
    _env = None

    @property
    def env(self):
        """ Simple lazy loaders """
        if not self._env:
            self._env = Environment(loader=FileSystemLoader(JinjaRenderer.search_path))
        return self._env

    def render(self, nodes, g_context):
        buildup = ""
        for n in nodes:
            template = self.env.get_template(n.template)
            buildup += template.render(n.get_context(g_context))
        return buildup
