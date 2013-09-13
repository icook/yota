import unittest
import yota
from yota.validators import *
from yota.nodes import *
from yota.exceptions import *
from copy import copy, deepcopy


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
            ('_node_list', [], [EntryNode(_attr_name='test')], True),
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
            class TForm(yota.Form):
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
        class TForm(yota.Form):
            start = EntryNode()
            close = EntryNode()

            t = EntryNode()
            _t_valid = yota.Check(
                MinLengthValidator(5, message="Darn"), 't')

        test = TForm()
        assert(isinstance(test.start, EntryNode))
        assert(isinstance(test.close, EntryNode))
        assert(test._node_list[0]._attr_name is 'start')
        assert(test._node_list[2]._attr_name is 'close')

    def test_node_order_prev(self):
        """ is node order being properly preserved, attr preserved, _node_list populated """
        one = EntryNode()
        two = EntryNode()
        three = EntryNode()
        class TForm(yota.Form):
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

    def test_blueprint(self):
        """ make sure forms can be used inside of forms """
        class TForm(yota.Form):
            something = EntryNode()
            other = EntryNode()
            thing = EntryNode()

        class BForm(yota.Form):
            first = EntryNode()
            second = TForm
            third = EntryNode()

        test = BForm()

        # attribute preservation
        assert(test.something._attr_name == "something")
        assert(test.other._attr_name == "other")
        assert(test.thing._attr_name == "thing")

        # assert correct order preservation
        assert(test._node_list[1]._attr_name == "first")
        assert(test._node_list[2]._attr_name == "something")
        assert(test._node_list[5]._attr_name == "third")


    #################################################################
    # Test core functionality of Form class
    def test_error_header(self):
        """ tests the validate_render methods use of success_header_generate """
        class TForm(yota.Form):
            t = EntryNode(validators=RequiredValidator())

            def error_header_generate(self, errors, block):
                self.start.add_error({'message': 'This is a very specific error'})

        test = TForm()
        success, render = test.validate_render({'t': ''})
        assert(success is False)
        assert('This is a very specific error' in render)

    def test_success_header(self):
        """ success header generation """

        class TForm(yota.Form):
            t = EntryNode()

            def success_header_generate(self):
                self.start.add_error({'message': 'something else entirely'})
                return {'message': 'something....'}

        test = TForm()
        success, json = test.json_validate({
            't': 'something',
            '_visited_names': '("t")',
            'submit_action': 'true'},
            raw=True)
        assert(success is True)
        assert('success_blob' in json)
        assert('something..' in json['success_blob']['message'])
        assert('success_ids' in json)

        # testing validate render portion
        success, render = test.validate_render({'t': 'something'})
        assert(success is True)
        assert('success_blob' in json)
        assert('something else entirely' in render)

    def test_validator_shorthand(self):
        """ Properly test many flexible shorthands """
        nl = [
            MinLengthValidator(5),
            (MinLengthValidator(5), ),
            [MinLengthValidator(5), ],
            [],
            Check(MinLengthValidator(5), 't'),
            [Check(MinLengthValidator(5), 't'), ],
            [Check(MinLengthValidator(5), 't'), MinLengthValidator(5)],
            (Check(MinLengthValidator(5)), MinLengthValidator(5)),
        ]
        # Since we're going to resolve the Checks again, easier to duplicate
        # them
        nl2 = deepcopy(nl)
        valid_list = [1, 1, 1, 0, 1, 1, 2, 2]
        for i, node in enumerate(nl):
            print("Testing shorthand scenario #" + str(i))
            class TForm(yota.Form):
                t = EntryNode(validators=node)
            test = TForm()
            test._parse_shorthand_validator(test.t)
            assert(len(test._validation_list) >= valid_list[i])
            block, err_list = test._gen_validate({'t': ''})
            if valid_list[i] > 0:
                assert(len(err_list[0].errors) >= valid_list[i])
            else:
                assert(len(err_list) == 0)

        for i, node in enumerate(nl2):
            # Now make sure passing as attr works
            print("Testing shorthand attr scenario #" + str(i))
            class TForm(yota.Form):
                class MyNode(yota.nodes.EntryNode):
                    validators = node
                t = MyNode()

            test = TForm()
            block, err_list = test._gen_validate({'t': 'a'})
            assert(len(test._validation_list) >= valid_list[i])
            if valid_list[i] > 0:
                assert(len(err_list[0].errors) >= valid_list[i])
            else:
                assert(len(err_list) == 0)


    ##################################################################
    # Coverage for utility functions, helpers
    def test_json_validation_update(self):
        """ updating of json return values to the header works properly """
        test = yota.Form()
        test._last_raw_json = {'success_blob': {}}
        ret = test.update_success({'add': 'me'}, raw=True)
        assert('add' in ret['success_blob'])
        ret = test.update_success({'those': 'are'})
        assert('those' in ret)
        assert('success_blob' in ret)

    def test_render_validation_update(self):
        """ updating of render return values to the header works properly """
        test = yota.Form()
        test.start.add_error({})
        test._last_valid = 'render'
        ret = test.update_success({'message': 'something'})
        assert('something' in ret)

    def test_data_by_attr_name(self):
        """ Data by attr and by name functions as expected """
        class TForm(yota.Form):
            t = EntryNode()

        test = TForm()
        test.t.data = 'something'
        test.t.name = 'two'

        assert('t' in test.data_by_attr())
        assert('two' in test.data_by_name())

    def test_data_by_attr_name(self):
        """ Data by attr and by name functions as expected """
        class TForm(yota.Form):
            t = EntryNode()

        test = TForm()
        test.t.data = 'something'
        test.t.name = 'two'

        assert('t' in test.data_by_attr())
        assert('two' in test.data_by_name())

    def test_dynamic_insert(self):
        """ insert_after test, and subsequently insert itself """
        class TForm(yota.Form):
            t = EntryNode()

        test = TForm()
        # Test one that hits the mark and finds t
        test.insert_after('t', EntryNode(_attr_name='t2'))
        assert(test._node_list[2]._attr_name == 't2')
        # Test one that goes to the bottom, no t4
        test.insert_after('t4', EntryNode(_attr_name='t3'))
        assert(test._node_list[4]._attr_name == 't3')

    def test_insert_validator(self):
        """ insert functions test plus special cases """
        test = yota.Form()
        tch = Check(RequiredValidator(), 't')
        tch2 = Check(MinLengthValidator(5), 't')
        tch3 = Check(MaxLengthValidator(5), 't')
        self.assertRaises(TypeError, test.insert_validator, ' ')
        test.insert_validator(tch)
        assert(test._validation_list[0] is tch)

        # make sure lists work as well
        test.insert_validator([tch2, tch3])
        assert(test._validation_list[1] is tch2)
        assert(test._validation_list[2] is tch3)

        # And tuples just to be over-thorough...
        test = yota.Form()
        test.insert_validator((tch, tch3))
        assert(test._validation_list[0] is tch)
        assert(test._validation_list[1] is tch3)

    def test_insert_special(self):
        """ insert functions test plus special cases """
        test = yota.Form()
        test.insert(0, EntryNode(_attr_name='test1'))
        assert(hasattr(test, 'test1'))
        assert(test._node_list[0]._attr_name == 'test1')
        test.insert(-1, EntryNode(_attr_name='test2'))
        assert(hasattr(test, 'test2'))
        assert(test._node_list[3]._attr_name == 'test2')
        test.insert(2, EntryNode(_attr_name='test3'))
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

        class TForm(yota.Form):
            t = EntryNode()
            _t_valid = yota.Check(RequiredValidator(message="Darn"), 't')

        test = TForm()
        success, response = test.json_validate({'t': '', '_visited_names': '{"t": true}'},
                                      piecewise=True)
        assert('Darn' in response)

    def test_piecewise_submit(self):
        """ a piecewise submit that is failing visited validators won't pass on
        submit"""

        class TForm(yota.Form):
            t = EntryNode()
            _t_valid = yota.Check(MinLengthValidator(5), 't')

        test = TForm()
        success, json = test.json_validate({'t': '',
            '_visited_names': '("t")',
            'submit_action': 'true'},
            piecewise=True,
            raw=True)
        assert(success is False)
        assert(len(json['errors']) > 0)

    def test_piecewise_novisit(self):
        """ any non-visited nodes cause submission to block """
        class TForm(yota.Form):
            t = EntryNode()
            _t_valid = yota.Check(MinLengthValidator(5), 't')

        test = TForm()
        block, invalid = test._gen_validate(
            {'t': '', '_visited_names': '{}'},
            piecewise=True)

        assert(block is True)
        assert(len(invalid) == 0)

    def test_piecewise_nosubmit(self):
        """ even with no errors and all visited, piecewise fails without submit """
        test = yota.Form()
        success, json = test.json_validate(
            {'_visited_names': '{}', 'submit_action': False},
            piecewise=True,
            raw=True)

        assert(success is False)
        assert(json['block'] is True)

    def test_piecewise_exc(self):
        """ validation will throw an exception without passing visited nodes """
        test = yota.Form()
        self.assertRaises(AttributeError, test._gen_validate, {}, piecewise=True)

    ######################################################################
    # Regular validation
    def test_valid_render_success(self):
        """ validate render method returns true for success when it's supposed to """
        assert(yota.Form().validate_render({})[0] is True)

    def test_validate_reg(self):
        """ regular validate meth works properly """
        class TForm(yota.Form):
            t = EntryNode()
            _t_valid = yota.Check(
                MinLengthValidator(5, message="Darn"), 't')

        test = TForm()
        success, ret = test.validate({'t': 'adfasdfasdf'})
        assert(success is True)
        assert(len(ret) == 0)
        success, ret = test.validate({'t': ''})
        assert(len(ret) > 0)
        assert(success is False)

    def test_non_blocking(self):
        """ ensure that a non-blocking validators validation is successful """
        class TForm(yota.Form):
            t = EntryNode()
            _t_valid = yota.Check(
                NonBlockingDummyValidator(), 't')

        test = TForm()
        block, invalid = test._gen_validate({'t': 'toolong'})
        assert(block is False)

    def test_bad_validator(self):
        """ malformed checks need to throw an exception """
        class TForm(yota.Form):
            t = EntryNode()
            _t_valid = yota.Check('fgsdfg', 't')

        test = TForm()
        self.assertRaises(
            NotCallableException, test._gen_validate, {'t': 'toolong'})

    ###############################################################
    # Testing Exceptions / Checking For core form functions
    def test_override_start_close_exc(self):
        # Test the start node
        def make_class():
            class TForm(yota.Form): start = ''
        self.assertRaises(AttributeError, make_class)

        # and the close node
        def make_class():
            class TForm(yota.Form): close = ''
        self.assertRaises(AttributeError, make_class)

    def test_node_attr_safety(self):
        """ Ensure safe node _attr_names """

        def stupid_2_6():
            class TForm(yota.Form):
                name = EntryNode()
            TForm()

        self.assertRaises(AttributeError, stupid_2_6)
        f = yota.Form()
        self.assertRaises(AttributeError, f.insert, 0, EntryNode())
        self.assertRaises(
            AttributeError, f.insert, 0, EntryNode(_attr_name='name'))
        self.assertRaises(AttributeError,
                          f.insert,
                          0,
                          EntryNode(_attr_name='g_context'))

    def test_update_success_exc(self):
        """ update success bounds checking verif """
        test = yota.Form()
        test._last_valid = 'render'
        self.assertRaises(IndexError, test.update_success, {'those': 'are'})
        delattr(test, 'start')
        self.assertRaises(AttributeError, test.update_success, {'those': 'are'})
