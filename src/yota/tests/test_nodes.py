import unittest
import yota
from yota.validators import *
from yota.nodes import *
from yota.exceptions import *


class TestNode(unittest.TestCase):
    def test_required(self):
        """ required node attribute properly raise on render """
        class TForm(yota.Form):
            t = ListNode()

        test = TForm()
        self.assertRaises(InvalidContextException, test.render)

    def test_ignores(self):
        """ _ignores doesn't pass to rendering context """
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
        """ Make sure we can pass attributes through the class """
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

class TestNodeSpecific(unittest.TestCase):
    """ Tests specific node behaviour for builtin nodes that have code
    associated with them """

    def test_checknode(self):
        """ checkbox node should return false if name not in return data """
        class TForm(yota.Form):
            t = CheckNode()

        test = TForm()
        block, invalid = test._gen_validate(
            {'_visited_names': '{}'}, piecewise=True)
        assert(test.t.data is False)

    def test_checkgroup(self):
        """ checkbox group data extraction works as intended """
        class TForm(yota.Form):
            t = CheckGroupNode(boxes=[('test', 'something'),
                                   ('this', 'else'),
                                   ('one', 'is')
                                   ])

        test = TForm()
        block, invalid = test._gen_validate(
            {'_visited_names': '["test", "this"]',
             'test': 'checked',
             'this': 'checked'},
            piecewise=True)

        assert(len(test.t.data) == 2)

        ident = test.t.json_identifiers()
        assert(len(ident['elements']) == 3)


if __name__ == '__main__':
    unittest.main()
