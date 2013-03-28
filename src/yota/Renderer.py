from jinja2 import Environment, PackageLoader

class Renderer(object):
    search_path = []

    def __init__(self):
        self.env = Environment(loader=PackageLoader('yourapplication', 'templates'))

    def render(self):
		pass
