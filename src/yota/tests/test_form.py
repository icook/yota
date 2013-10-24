from yota import Check, Form, Listener, Blueprint
import yota.validators as validators
import yota.nodes as nodes
from yota.exceptions import *

from copy import copy, deepcopy
import unittest

class TestForms(unittest.TestCase):
    """ Covers core Form functionality with the exception of validator logic """

    ####################################################################
    # Testing for passing of values being copied/not copied properly between
    # attributes, arguments and parameters
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
            ('g_context', copy(td), copy(td2), True),
            ('context', copy(td), copy(td2), True),
            ('_node_list', [], [nodes.Entry(_attr_name='test')], True),
            ('_validation_list', copy(tl), copy(td2), True),
            ('my_custom_attr2', copy(tl), copy(tl2), True),
            ('start_template', 'customtem', 'close', False),
            ('close_template', 'customtem', 'start', False),
            ('name', 'customname', 'othername', False),
            ('auto_start_close', True, False, False),
            ('title', 'thistitle', 'notthisone', False),
            ('custom', 'thistitle', 'notthisone', False)
        ]
        for key, class_val, kwarg_val, mutable in tests:
            print("Running test for key type " + key)
            class TForm(Form):
                pass
            # set our class attribute
            setattr(TForm, key, class_val)

            if mutable:
                tester = TForm()
                tester2 = TForm()
                # Make sure a copy is happening for our mutable types
                assert(getattr(TForm, key) is not getattr(tester, key))
                assert(getattr(tester2, key) is not getattr(tester, key))

            tester = TForm(**{key: kwarg_val})
            # Ensure exactly our desired copy/override semantics with kwargs
            assert(getattr(TForm, key) is not getattr(tester, key))
            assert(getattr(TForm, key) != getattr(tester, key))
            assert(class_val is not getattr(tester, key))
            assert(class_val != getattr(tester, key))

    def test_override_start_close(self):
        class TForm(Form):
            start = nodes.Entry()
            close = nodes.Entry()

            t = nodes.Entry()
            _t_valid = Check(validators.MinLength(5, message="Darn"), 't')

        test = TForm()
        assert(isinstance(test.start, nodes.Entry))
        assert(isinstance(test.close, nodes.Entry))
        assert(test._node_list[0]._attr_name is 'start')
        assert(test._node_list[2]._attr_name is 'close')

    def test_node_order_prev(self):
        """ is node order being properly preserved, attr preserved, _node_list populated """
        one = nodes.Entry()
        two = nodes.Entry()
        three = nodes.Entry()
        class TForm(Form):
            something = one
            other = two
            thing = three

        test = TForm()
        # In the class object
        assert(TForm._node_list[0] is one)
        assert(TForm._node_list[1] is two)
        assert(TForm._node_list[2] is three)

        # In its instances
        assert(test._node_list[1]._attr_name == one._attr_name)
        assert(test._node_list[2]._attr_name == two._attr_name)
        assert(test._node_list[3]._attr_name == three._attr_name)

        # attribute preservation
        assert(test.something._attr_name == one._attr_name)
        assert(test.other._attr_name == two._attr_name)
        assert(test.thing._attr_name == three._attr_name)

    def test_blueprint_nodes(self):
        """ make sure forms can be used inside of forms """
        class TForm(Form):
            something = nodes.Entry()
            other = nodes.Entry()
            thing = nodes.Entry()

        class BForm(Form):
            first = nodes.Entry()
            second = Blueprint(TForm)
            third = nodes.Entry()

        test = BForm()

        # attribute preservation
        assert(test.something._attr_name == "something")
        assert(test.other._attr_name == "other")
        assert(test.thing._attr_name == "thing")

        # assert correct order preservation
        assert(test._node_list[1]._attr_name == "first")
        assert(test._node_list[2]._attr_name == "something")
        assert(test._node_list[5]._attr_name == "third")

    def test_blueprint_events(self):
        """ ensure events get transferred properly """
        def testing():
            print("nothing")

        class TForm(Form):
            test = Listener("something", testing)
            test2 = Listener("else", testing)

        class BForm(Form):
            test3 = Listener("else", testing)
            test4 = Blueprint(TForm)

        test = BForm()

        # make sure the keys are there
        assert("something" in test._event_lists)
        assert("else" in test._event_lists)

        # assert correct order preservation
        assert(len(test._event_lists["something"]) == 1)
        assert(len(test._event_lists["else"]) == 2)

    def test_blueprint_validators(self):
        """ ensure events get transferred properly """
        class TForm(Form):
            main = nodes.Entry(validators=validators.MinLength(5))
            other_name_val = Check(validators.MinLength(10), "main")

        class BForm(Form):
            test4 = Blueprint(TForm)

        test = BForm()

        assert(len(test._validation_list) == 1)
        assert(test._validation_list[0].callable.min_length == 10)

    #################################################################
    # Test core functionality of Form class
    def test_error_header(self):
        """ tests the validate method use of success_header_generate """
        class TForm(Form):
            t = nodes.Entry(validators=validators.Required())

            def error_header_generate(self, errors):
                self.start.add_msg({'message': 'This is a very specific error'})
                return {'message': 'Other error'}

        test = TForm()
        success, render = test.validate_render({'t': ''})
        assert(success is False)
        assert('This is a very specific error' in render)
        assert('Other error' in render)

    def test_parent_form(self):
        """ existence of _parent_form being populated"""
        class TForm(Form):
            t = nodes.Entry()

        test = TForm()
        test.insert_node(1, nodes.Entry(_attr_name="testing"))
        assert(test.t._parent_form is test)
        assert(test.testing._parent_form is test)

    def test_success_header(self):
        """ success header generation """

        class TForm(Form):
            t = nodes.Entry()

            def success_json_generate(self):
                self.start.add_msg({'message': 'something else entirely'})
                return {'message': 'something....'}

        test = TForm()
        success, json = test.validate_json({
            't': 'something',
            '_visited_names': '("t")',
            'submit_action': 'true'},
            raw=True)
        assert(success is True)
        assert('success_blob' in json)
        assert('something..' in json['success_blob']['message'])
        assert('success_ids' in json)

    def test_validator_shorthand(self):
        """ Properly test many flexible shorthands """
        nl = [
            validators.MinLength(5),
            (validators.MinLength(5), ),
            [validators.MinLength(5), ],
            [],
            Check(validators.MinLength(5), 't'),
            [Check(validators.MinLength(5), 't'), ],
            [Check(validators.MinLength(5), 't'), validators.MinLength(5)],
            (Check(validators.MinLength(5)), validators.MinLength(5)),
        ]
        # Since we're going to resolve the Checks again, easier to duplicate
        # them
        nl2 = deepcopy(nl)
        valid_list = [1, 1, 1, 0, 1, 1, 2, 2]
        for i, node in enumerate(nl):
            print("Testing shorthand scenario #" + str(i))
            class TForm(Form):
                t = nodes.Entry(validators=node)
            test = TForm()
            test._parse_shorthand_validator(test.t)
            assert(len(test._validation_list) >= valid_list[i])
            block, err_list = test._gen_validate({'t': ''}, internal=True)
            if valid_list[i] > 0:
                assert(len(err_list[0].msgs) >= valid_list[i])
            else:
                assert(len(err_list) == 0)

        for i, node in enumerate(nl2):
            # Now make sure passing as attr works
            print("Testing shorthand attr scenario #" + str(i))
            class TForm(Form):
                class MyNode(nodes.Entry):
                    validators = node
                t = MyNode()

            test = TForm()
            block, err_list = test._gen_validate({'t': 'a'}, internal=True)
            assert(len(test._validation_list) >= valid_list[i])
            if valid_list[i] > 0:
                assert(len(err_list[0].msgs) >= valid_list[i])
            else:
                assert(len(err_list) == 0)


    ##################################################################
    # Coverage for utility functions, helpers
    def test_data_by_attr_name(self):
        """ Data by attr and by name functions as expected """
        class TForm(Form):
            t = nodes.Entry()

        test = TForm()
        test.t.data = 'something'
        test.t.name = 'two'

        assert('t' in test.data_by_attr())
        assert('two' in test.data_by_name())

    def test_form_resolve(self):
        """ resolve all should function as expected """
        class TForm(Form):
            t = nodes.Entry()

        test = TForm()
        test.resolve_all({'t': 'Something'})
        assert test.t.data == 'Something'

    def test_dynamic_insert(self):
        """ insert_after test, and subsequently insert itself """
        class TForm(Form):
            t = nodes.Entry()

        test = TForm()
        # Test one that hits the mark and finds t
        test.insert_node_after('t', nodes.Entry(_attr_name='t2'))
        assert(test._node_list[2]._attr_name == 't2')
        # Test one that goes to the bottom, no t4
        test.insert_node_after('t4', nodes.Entry(_attr_name='t3'))
        assert(test._node_list[4]._attr_name == 't3')

    def test_insert_validator(self):
        """ insert functions test plus special cases """
        test = Form()
        tch = Check(validators.Required(), 't')
        tch2 = Check(validators.MinLength(5), 't')
        tch3 = Check(validators.MaxLength(5), 't')
        self.assertRaises(TypeError, test.insert_validator, ' ')
        test.insert_validator(tch)
        assert(test._validation_list[0] is tch)

        # make sure lists work as well
        test.insert_validator([tch2, tch3])
        assert(test._validation_list[1] is tch2)
        assert(test._validation_list[2] is tch3)

        # And tuples just to be over-thorough...
        test = Form()
        test.insert_validator((tch, tch3))
        assert(test._validation_list[0] is tch)
        assert(test._validation_list[1] is tch3)

    def test_insert_special(self):
        """ insert functions test plus special cases """
        test = Form()
        test.insert_node(0, nodes.Entry(_attr_name='test1'))
        assert(hasattr(test, 'test1'))
        assert(test._node_list[0]._attr_name == 'test1')
        test.insert_node(-1, nodes.Entry(_attr_name='test2'))
        assert(hasattr(test, 'test2'))
        assert(test._node_list[3]._attr_name == 'test2')
        test.insert_node(2, nodes.Entry(_attr_name='test3'))
        assert(hasattr(test, 'test3'))
        assert(test._node_list[2]._attr_name == 'test3')


class TestFormValidation(unittest.TestCase):
    """ Coverage for the 4 main validation functions in Form """

    ######################################################################
    # JSON/Piecewise specific methods
    def test_json_validation(self):
        """ json piecewise works properly """
        # TODO: Needs significant expansion. Severl more assertions at least,
        # and probably a few more scenarios

        class TForm(Form):
            t = nodes.Entry()
            _t_valid = Check(validators.Required(message="Darn"), 't')

        test = TForm()
        success, json = test.validate_json({'t': '', '_visited_names': '{"t": true}'},
                                      piecewise=True)
        assert('Darn' in json)

    def test_piecewise_submit(self):
        """ a piecewise submit that is failing visited validators won't pass on
        submit"""

        class TForm(Form):
            t = nodes.Entry()
            _t_valid = Check(validators.MinLength(5), 't')

        test = TForm()
        success, json = test.validate_json(
            {'t': '',
             '_visited_names': '{"t": true}',
             'submit_action': 'true'},
            piecewise=True,
            raw=True)
        assert(success is False)
        assert(len(json['msgs']) > 0)

    def test_piecewise_novisit(self):
        """ any non-visited nodes cause submission to block """
        class TForm(Form):
            t = nodes.Entry()
            _t_valid = Check(validators.MinLength(5), 't')

        test = TForm()
        success, invalid = test._gen_validate(
            {'t': '', '_visited_names': '{}'},
            piecewise=True, internal=True)

        assert(success is False)
        assert(len(invalid) == 0)

    def test_piecewise_nosubmit(self):
        """ even with no errors and all visited, piecewise fails without submit """
        test = Form()
        success, json = test.validate_json(
            {'_visited_names': '{}', 'submit_action': False},
            piecewise=True,
            raw=True)

        assert(success is False)
        assert(json['success'] is False)

    def test_piecewise_exc(self):
        """ validation will throw an exception without passing visited nodes """
        test = Form()
        self.assertRaises(AttributeError, test._gen_validate, {}, piecewise=True)

    def test_success_insert(self):
        """ the dedicated success_insert function """
        test = Form()
        test._submit_action = True
        test.set_json_success(redirect='home')
        json = test.render_json({'submit_action': 'true'}, raw=True)

        assert('redirect' in json['success_blob'])

    ######################################################################
    # Regular validation
    def test_valid_render_success(self):
        """ validate render method returns true for success when it's supposed to """
        assert(Form().validate_render({})[0] is True)

    def test_validate_reg(self):
        """ regular validate meth works properly """
        class TForm(Form):
            t = nodes.Entry()
            _t_valid = Check(
                validators.MinLength(5, message="Darn"), 't')

        test = TForm()
        success, ret = test.validate({'t': 'adfasdfasdf'}, internal=True)
        assert(success is True)
        assert(len(ret) == 0)
        success, ret = test.validate({'t': ''}, internal=True)
        assert(len(ret) > 0)
        assert(success is False)

    def test_non_blocking(self):
        """ ensure that a non-blocking validators validation is successful """
        class TForm(Form):
            t = nodes.Entry()
            _t_valid = Check(
                validators.NonBlockingDummy(), 't')

        test = TForm()
        success, invalid = test._gen_validate({'t': 'toolong'}, internal=True)
        assert(success is True)

    def test_bad_validator(self):
        """ malformed checks need to throw an exception """
        class TForm(Form):
            t = nodes.Entry()
            _t_valid = Check('fgsdfg', 't')

        test = TForm()
        self.assertRaises(
            NotCallableException, test._gen_validate, {'t': 'toolong'})

    ###############################################################
    # Testing Exceptions / Checking For core form functions
    def test_override_start_close_exc(self):
        # Test the start node
        def make_class():
            class TForm(Form): start = ''
        self.assertRaises(AttributeError, make_class)

        # and the close node
        def make_class():
            class TForm(Form): close = ''
        self.assertRaises(AttributeError, make_class)

    def test_node_attr_safety(self):
        """ Ensure safe node _attr_names """

        def stupid_2_6():
            class TForm(Form):
                name = nodes.Entry()
            TForm()

        self.assertRaises(AttributeError, stupid_2_6)
        f = Form()
        self.assertRaises(AttributeError, f.insert_node, 0, nodes.Entry())
        self.assertRaises(
            AttributeError, f.insert_node, 0, nodes.Entry(_attr_name='name'))
        self.assertRaises(AttributeError,
                          f.insert_node,
                          0,
                          nodes.Entry(_attr_name='g_context'))
