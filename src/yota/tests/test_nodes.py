import unittest
import yota
from yota.validators import *
from yota.nodes import *
from yota.exceptions import *
from copy import copy


class TestNode(unittest.TestCase):
    def test_class_override(self):
        """ ensure that a class attribute can be overriden by kwarg. Also
        ensure mutable class attributes are copied on init """

        # setup some test mutable types
        td = {'something': 'else'}
        td2 = {'something': 'else', 'entirely': 'different'}
        tl = ['this', 'is', 'a', 'list']
        tl2 = ['this', 'is']
        # Now setup our test data. We want to ensure that a value set as a
        # default as a class attr is properly overriden by using the kwarg
        tests = [
            ('_ignores', copy(tl), copy(td2), True),
            ('_requires', copy(tl), copy(td2), True),
            ('my_custom_attr2', copy(tl), copy(tl2), True),
            ('template', 'customtem', 'close', False),
            ('label', 'customname', 'othername', False),
            ('_attr_name', 'something', 'else', False),
            ('my_custom_attr', 'something2', 'else2', False)
        ]
        for key, class_val, kwarg_val, mutable in tests:
            print("Running test for key type " + key)
            class TNode(yota.nodes.Node):
                pass
            # set our class attribute
            setattr(TNode, key, class_val)

            if mutable:
                tester = TNode()
                tester2 = TNode()
                # Make sure a copy is happening for our mutable types
                assert(getattr(TNode, key) is not getattr(tester, key))
                assert(getattr(tester2, key) is not getattr(tester, key))

            tester = TNode(**{key: kwarg_val})
            # Ensure exactly our desired copy/override semantics with kwargs
            assert(getattr(TNode, key) is not getattr(tester, key))
            assert(getattr(TNode, key) != getattr(tester, key))
            assert(class_val is not getattr(tester, key))
            assert(class_val != getattr(tester, key))

    def test_validate_class_attr(self):
        """ Test whether setting validator as class attributes of Nodes gets
        correctly passed """
        # TODO: Needs to be reworked similar to the comprehensive test in Form
        class TForm(yota.Form):
            class MyNode(yota.nodes.EntryNode):
                validators = MinLengthValidator(5, message="Darn")
            t = MyNode()

        test = TForm()
        test._parse_shorthand_validator(test.t)
        assert(len(test._validation_list) > 0)
        assert(isinstance(test._validation_list[0].validator,
                          MinLengthValidator))

        # ensure that we can still add multiples through iterable types
        class TForm2(yota.Form):
            class MyNode(yota.nodes.EntryNode):
                validators = [MinLengthValidator(5, message="Darn"),
                                MaxLengthValidator(5, message="Darn")]
            t = MyNode()

        test = TForm2()
        test._parse_shorthand_validator(test.t)
        assert(len(test._validation_list) > 1)

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

    def test_data_resolver(self):
        """ default data resolution implemented """
        class TForm(yota.Form):
            t = EntryNode()
            _t_valid = yota.Check(
                RequiredValidator(message="Darn"), target='t')

        test = TForm()
        block, invalid = test._gen_validate({'t': 'testing'})
        assert(test.t.data == 'testing')

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
