import unittest
import yota
from yota.validators import *
from yota.nodes import *
from yota.exceptions import *
import copy


class TestForms(unittest.TestCase):

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
            ('_node_list', copy(td), copy(td2), True),
            ('_validation_list', copy(tl), copy(td2), True),
            ('start_template', 'customtem', 'close', False),
            ('close_template', 'customtem', 'start', False),
            ('name', 'customname', 'othername', False),
            ('auto_start_close', True, False, False),
            ('title', 'thistitle', 'notthisone', False)
        ]
        for key, class_val, kwarg_val, mutable in t1:
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

            tester = TForm({key: kwarg_val})
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

    #################################################################
    # Test core functionality of Form class

    def test_piecewise_success_header(self):
        """ Piecewise success header generation """

        class TForm(yota.Form):
            t = EntryNode()

            def success_header_generate(self):
                return {'message': 'something....'}

        test = TForm()
        success, json = test.json_validate({'t': 'something',
                                             '_visited_names': '("t")',
                                             'submit_action': 'true'},
                                            piecewise=True)
        assert(success is True)

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
        valid_list = [1, 1, 1, 0, 1, 1, 2, 2]
        for i, node in enumerate(nl):
            print "Testing shorthand scenario #" + str(i)
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

    def test_error_header(self):
        """ tests the validate_render methods use of success_header_generate """
        class TForm(yota.Form):
            t = EntryNode(validators=RequiredValidator())

            def error_header_generate(self, errors, block):
                self.start.add_error({'message': 'This is a very specific error'})

        test = TForm()
        success, node_list = test.validate_render({'t': ''})
        assert(hasattr(test.start, 'errors'))
        assert('This is a very specific error' in node_list)

    ######################################################################
    # Test facets of the validation methods in the Form class

    def test_piecewise_novisit(self):
        """ any non-visited nodes cause submission to block """
        class TForm(yota.Form):
            t = EntryNode()
            _t_valid = yota.Check(
                MinLengthValidator(5, message="Darn"), 't')

        test = TForm()
        block, invalid = test._gen_validate({'t': '', '_visited_names': '{}'}, piecewise=True)

        assert(block is True)
        assert(len(invalid) == 0)

    def test_non_blocking(self):
        """ ensure that a non-blocking validators validation is successful """
        class TForm(yota.Form):
            t = EntryNode()
            _t_valid = yota.Check(
                NonBlockingDummyValidator(), 't')

        test = TForm()
        block, invalid = test._gen_validate({'t': 'toolong'})
        assert(block is False)

    def test_piecewise_submit(self):
        """ Make sure a submit that is failing validators won't pass """

        class TForm(yota.Form):
            t = EntryNode()
            _t_valid = yota.Check(
                MinLengthValidator(5, message="Darn"), 't')

        test = TForm()
        success, invalid = test.json_validate({'t': '',
                                             '_visited_names': '("t")',
                                             'submit_action': 'true'},
                                            piecewise=True)
        assert(success is False)
        assert(len(invalid) > 0)

    def test_valid_render_success(self):
        """ validate render method returns true for success when it's supposed to """
        assert(yota.Form().validate_render({})[0] is True)

    def test_piecewise_block(self):
        """ piecewise needs to block when any validators don't pass """
        # TODO: Should be expanded a fair bit
        class TForm(yota.Form):
            t = EntryNode()
            _t_valid = yota.Check(RequiredValidator(message="Darn"), 't')
            _t_length = yota.Check(MaxLengthValidator(4), 't')

        test = TForm()
        block, invalid = test._gen_validate({'t': 'toolong', '_visited_names': '{"t": true}'},
                                            piecewise=True)
        assert(block is True)

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

    ###############################################################
    # Testing Exceptions / Checking

    def test_override_start_close_exc(self):
        # Test the start node
        class TForm(yota.Form):
            start = ''
        self.assertRaises(AttributeError, TForm)

        # and the close node
        class TForm(yota.Form):
            close = ''
        self.assertRaises(AttributeError, TForm)

    def test_bad_validator(self):
        """ malformed checks need to throw an exception """
        class TForm(yota.Form):
            t = EntryNode()
            _t_valid = yota.Check('fgsdfg', 't')

        test = TForm()
        self.assertRaises(NotCallableException,
                          test._gen_validate, {'t': 'toolong'})

    def test_node_attr_safety(self):
        """ Ensure safe node _attr_names """

        def stupid_2_6():
            class TForm(yota.Form):
                name = EntryNode()
            TForm()

        self.assertRaises(AttributeError, stupid_2_6)
        f = yota.Form()
        self.assertRaises(AttributeError, f.insert, 0, EntryNode())
        self.assertRaises(AttributeError, f.insert, 0, EntryNode(_attr_name='name'))
        self.assertRaises(AttributeError,
                          f.insert,
                          0,
                          EntryNode(_attr_name='g_context'))

    def test_piecewise_exc(self):
        """ validation will throw an exception without passing visited nodes """
        test = yota.Form()
        self.assertRaises(AttributeError, test._gen_validate, {}, piecewise=True)

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

    def test_get_by_attr(self):
        class TForm(yota.Form):
            t = EntryNode()
            _t_valid = yota.Check(
                MinLengthValidator(5, message="Darn"), 't')

        test = TForm()
        assert(test.get_by_attr('t') is not None)
        self.assertRaises(AttributeError, test.get_by_attr, 'g_context')
        self.assertRaises(AttributeError, test.get_by_attr, 'dsafkjnasdf')
