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
        """ Ensure _ignores and _requires can be overridden as class attributes
        properly """
        t = EntryNode(_ignores=['something'], _requires=['something_else'])

        assert('something' in t._ignores)
        assert('something_else' in t._requires)

if __name__ == '__main__':
    unittest.main()
