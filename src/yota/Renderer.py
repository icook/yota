from jinja2 import Environment, PackageLoader
import os

class Renderer(object):
    # automatically populate our search path with the default templates
    search_path = [os.path.dirname(os.path.realpath(__file__))]

    @property
    def env(self):
        """ Simple lazy loaders """
        if not self._env:
            self._env = Enviroment(loader=FileSystemLoader(self.search_path))
        return self._env

    def render(self, nodes, g_context):
        buildup = None
        for n in nodes:
            template = self.env.get_template(n.template)
            buildup += template.render(nodes.get_context(g_context))
        return buildup
