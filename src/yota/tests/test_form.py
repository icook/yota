import unittest
import yota
from yota.validators import *
from yota.nodes import *
from yota.exceptions import *


class TestForms(unittest.TestCase):
    """ Test key functionality of the forms """

    def test_override_start_close(self):
        """ Ensures that start and close can be properly switched out """
        class TForm(yota.Form):
            start = EntryNode()
            close = EntryNode()

        test = TForm()
        assert(isinstance(test.start, EntryNode))
        assert(isinstance(test.close, EntryNode))

    def test_override_start_close_exc(self):
        """ Tests the exceptions thrown if the start and close nodes are not
        nodes """
        # Test the start node
        class TForm(yota.Form):
            start = ''

        self.assertRaises(AttributeError,
                          TForm)

        # and the close node
        class TForm(yota.Form):
            close = ''

        self.assertRaises(AttributeError,
                          TForm)

    def test_dynamic_insert(self):
        """ Tests all edges of the insert function that allows addition of a new
        Node """
        class TForm(yota.Form):
            t = EntryNode()
            _t_valid = yota.Check(
                MinLengthValidator(5, message="Darn"), 't')

        test = TForm()
        test.insert_after('t', EntryNode(_attr_name='t2'))
        assert(test._node_list[2]._attr_name == 't2')
        test.insert_after('t4', EntryNode(_attr_name='t3'))
        assert(test._node_list[4]._attr_name == 't3')

    def test_error_header(self):
        """ Test that the error header method works as expected """
        class TForm(yota.Form):
            t = EntryNode()
            _t_valid = yota.Check(RequiredValidator(message="Darn"), 't')

            def error_header_generate(self, errors, block):
                self.start.add_error({'message': 'testo'})

        test = TForm()
        test.validate_render({'t': ''})
        assert(hasattr(test.start, 'errors'))

    def test_valid_render_success(self):
        """ Test to ensure that a renderer actually works uppon valid data """
        class TForm(yota.Form):
            t = EntryNode()
            _t_valid = yota.Check(RequiredValidator(message="Darn"), 't')

        test = TForm()
        assert(test.validate_render({'t': 'sdflkm'}) is True)

    def test_piecewise_block(self):
        """ Test that a piecewise validator will still block submission even
        when none of the data it is handed is invalid, yet is still missing some
        data from the submission """
        class TForm(yota.Form):
            t = EntryNode()
            _t_valid = yota.Check(RequiredValidator(message="Darn"), 't')
            b = EntryNode()
            _b_req = yota.Check(MinLengthValidator(5), 'b')

        test = TForm()
        block, invalid = test._gen_validate({'t': 'toolong'}, piecewise=True)
        assert(block is True)

    def test_auto_start_close(self):
        """ Make sure that disabling auto_start_close works """
        test = yota.Form(auto_start_close=False)
        assert(hasattr(test, 'start') is False)
        assert(hasattr(test, 'close') is False)

    def test_data_return(self):
        """ Test data return methods """
        class TForm(yota.Form):
            t = EntryNode(name='test')
            b = EntryNode(name='blob')
        test = TForm()
        test.t.data = 'no1'
        test.b.data = 'no2'
        output = test.data_by_name()
        assert('test' in output)
        assert(output['test'] == 'no1')
        assert('blob' in output)
        assert(output['blob'] == 'no2')
        output = test.data_by_attr()
        assert('t' in output)
        assert(output['t'] == 'no1')
        assert('b' in output)
        assert(output['b'] == 'no2')

class TestValidation(unittest.TestCase):
    """ Group together all the validation related tests, even if they're driven
    by validation methods through Form """

    def test_validator_shorthand(self):
        """ Test passing in validators (checks) as an attribute """
        class TForm(yota.Form):
            t = EntryNode(validators=MinLengthValidator(5,
                          message="Darn"))

        test = TForm()
        assert(len(test._validation_list) > 0)
        assert(isinstance(test._validation_list[0].validator,
                          MinLengthValidator))

    def test_json_validation(self):
        """ Ensure that a json validator properly returns errors when it's
        supposed to """
        class TForm(yota.Form):
            t = EntryNode()
            _t_valid = yota.Check(RequiredValidator(message="Darn"), 't')

        test = TForm()
        response = test.json_validate({'t': ''}, piecewise=True)
        assert('Darn' in response)

    def test_bad_validator(self):
        """ Tests to ensure that a non-callable validator throws the proper
        exception """
        class TForm(yota.Form):
            t = EntryNode()
            _t_valid = yota.Check('fgsdfg', 't')

        test = TForm()
        self.assertRaises(NotCallableException,
                          test._gen_validate, {'t': 'toolong'})

    def test_validate_reg(self):
        """ Test the plain validation function for proper operation """
        class TForm(yota.Form):
            t = EntryNode()
            _t_valid = yota.Check(
                MinLengthValidator(5, message="Darn"), 't')

        test = TForm()
        ret = test.validate({'t': 'adfasdfasdf'})
        assert(ret is True)
        invalid = test.validate({'t': ''})
        assert(len(invalid) > 0)

class TestExtra(unittest.TestCase):
    """ Non outward facing functionality """

    def test_get_by_attr(self):
        """ Tests an internal utility function to make sure it returns properly
        """
        class TForm(yota.Form):
            t = EntryNode()
            _t_valid = yota.Check(
                MinLengthValidator(5, message="Darn"), 't')

        test = TForm()
        # will return actual nodes
        assert(test.get_by_attr('t') is not None)
        # it won't return non-nodes
        assert(test.get_by_attr('g_context') is None)
        # it won't return non-existent attributes
        assert(test.get_by_attr('dsfglkn') is None)
