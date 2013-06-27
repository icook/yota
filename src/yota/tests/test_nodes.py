import unittest
import yota
from yota.validators import *
from yota.nodes import *
from yota.exceptions import *


class TestNode(unittest.TestCase):
    def test_required(self):
        """ Testing a required node attribute """
        class TForm(yota.Form):
            t = ListNode()

        test = TForm()
        self.assertRaises(InvalidContextException, test.render)

    def test_ignores(self):
        """ _ignores functionality check """
        class TForm(yota.Form):
            t = EntryNode()

        test = TForm()
        assert('template' not in test.t.get_context({}))

    def test_ignores_requires_override(self):
        """ Ensure _ignores and _requires can be overridden as kwargs
        properly """
        t = EntryNode(_ignores=['something'], _requires=['something_else'])

        assert('something' in t._ignores)
        assert('something_else' in t._requires)

    def test_attribute_pass(self):
        """ Make sure we can pass attributes through """
        class MyNode(yota.Node):
            _ignores = None
            _requires = list()
            validator = dict()
            something = True
            label = False

        t = MyNode()
        assert(t._ignores is None)
        assert(isinstance(t._requires, list))
        assert(isinstance(t.validator, dict))
        assert(t.something is True)
        assert(t.label is False)

if __name__ == '__main__':
    unittest.main()
