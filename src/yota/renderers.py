from jinja2 import Environment, FileSystemLoader
import os


class JinjaRenderer(object):
    # automatically populate our search path with the default templates
    search_path = [os.path.dirname(os.path.realpath(__file__)) +
            "/templates/jinja/"]
    _env = None
    suffix = ".html"

    @property
    def env(self):
        """ Simple lazy loaders """
        if not self._env:
            self._env = Environment(loader=FileSystemLoader(JinjaRenderer.search_path))
        return self._env

    def render(self, nodes, g_context):
        buildup = ""
        for node in nodes:
            template = self.env.get_template(node.template + self.suffix)
            buildup += template.render(node.get_context(g_context))
        return buildup
