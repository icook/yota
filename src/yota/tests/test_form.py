import unittest
import yota
from yota.validators import *
from yota.nodes import *
from yota.exceptions import *


class TestForms(unittest.TestCase):
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

    def test_override_start_close_exc(self):
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
        class TForm(yota.Form):
            t = EntryNode()
            _t_valid = yota.Check(
                MinLengthValidator(5, message="Darn"), 't')

        test = TForm()
        test.insert_after('t', EntryNode(_attr_name='t2'))
        assert(test._node_list[2]._attr_name == 't2')
        test.insert_after('t4', EntryNode(_attr_name='t3'))
        assert(test._node_list[4]._attr_name == 't3')

    def test_validator_shorthand(self):
        class TForm(yota.Form):
            t = EntryNode(validators=MinLengthValidator(5,
                          message="Darn"))

        test = TForm()
        assert(len(test._validation_list) > 0)
        assert(isinstance(test._validation_list[0].validator,
                          MinLengthValidator))

    def test_validator_shorthand_list(self):
        class TForm(yota.Form):
            t = EntryNode(validators=[MinLengthValidator(5,
                          message="Darn"), RequiredValidator()])

        test = TForm()
        assert(len(test._validation_list) > 0)
        assert(isinstance(test._validation_list[0].validator,
                          MinLengthValidator))
        block, invalid = test._gen_validate({'t': ''})


    def test_error_header(self):
        class TForm(yota.Form):
            t = EntryNode()
            _t_valid = yota.Check(RequiredValidator(message="Darn"), 't')

            def error_header_generate(self, errors, block):
                self.start.add_error({'message': 'testo'})

        test = TForm()
        test.validate_render({'t': ''})
        assert(hasattr(test.start, 'errors'))

    def test_valid_render_success(self):
        class TForm(yota.Form):
            t = EntryNode()
            _t_valid = yota.Check(RequiredValidator(message="Darn"), 't')

        test = TForm()
        assert(test.validate_render({'t': 'sdflkm'}) is True)

    def test_json_validation(self):
        class TForm(yota.Form):
            t = EntryNode()
            _t_valid = yota.Check(RequiredValidator(message="Darn"), 't')

        test = TForm()
        response = test.json_validate({'t': ''}, piecewise=True)
        assert('Darn' in response)

    def test_piecewise_block(self):
        class TForm(yota.Form):
            t = EntryNode()
            _t_valid = yota.Check(RequiredValidator(message="Darn"), 't')
            b = EntryNode()
            _b_req = yota.Check(MinLengthValidator(5), 'b')

        test = TForm()
        block, invalid = test._gen_validate({'t': 'toolong'}, piecewise=True)
        assert(block is True)

    def test_bad_validator(self):
        class TForm(yota.Form):
            t = EntryNode()
            _t_valid = yota.Check('fgsdfg', 't')

        test = TForm()
        self.assertRaises(NotCallableException,
                          test._gen_validate, {'t': 'toolong'})

    def test_validate_reg(self):
        class TForm(yota.Form):
            t = EntryNode()
            _t_valid = yota.Check(
                MinLengthValidator(5, message="Darn"), 't')

        test = TForm()
        ret = test.validate({'t': 'adfasdfasdf'})
        assert(ret is True)
        invalid = test.validate({'t': ''})
        assert(len(invalid) > 0)

    def test_auto_start_close(self):
        test = yota.Form(auto_start_close=False)
        assert(hasattr(test, 'start') is False)
        assert(hasattr(test, 'close') is False)

class TestExtra(unittest.TestCase):
    def test_get_by_attr(self):
        class TForm(yota.Form):
            t = EntryNode()
            _t_valid = yota.Check(
                MinLengthValidator(5, message="Darn"), 't')

        test = TForm()
        assert(test.get_by_attr('t') is not None)
        assert(test.get_by_attr('g_context') is None)
        assert(test.get_by_attr('dsfglkn') is None)
