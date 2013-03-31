class PostProcessor(object):
    """ A base class for all post processors. Post
    processors handle interoperability between different
    web development frameworks. """
    pass


class FlaskPostProcessor(object):
    def filter_post(self, postdict):
        return postdict
