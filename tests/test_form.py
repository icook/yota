import unittest
import yota
from yota.validators import *
from yota.nodes import *


class TestForms(unittest.TestCase):
    def test_override_start_close(self):
        class TForm(yota.Form):
            start = EntryNode()
            close = EntryNode()

            t = EntryNode()
            _t_valid = yota.Check(
                MinLengthValidator(5, message="Darn"), 't')

        test = TForm()
        test.render()
        assert(isinstance(test.start, EntryNode))

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

    def test_error_header(self):
        class TForm(yota.Form):
            t = EntryNode()
            _t_valid = yota.Check(RequiredValidator(message="Darn"), 't')

            def error_header_generate(self, errors, block):
                self.start.add_error({'message': 'testo'})

        test = TForm()
        test.validate_render({'t': ''})
        assert(hasattr(test.start, 'errors'))

    def test_json_validation(self):
        class TForm(yota.Form):
            t = EntryNode()
            _t_valid = yota.Check(RequiredValidator(message="Darn"), 't')

        test = TForm()
        response = test.json_validate({'t': ''}, piecewise=True)
        assert('Darn' in response)


class TestExtra(unittest.TestCase):
    def test_get_by_attr(self):
        class TForm(yota.Form):
            t = EntryNode()
            _t_valid = yota.Check(
                MinLengthValidator(5, message="Darn"), 't')

        test = TForm()
        assert(test.get_by_attr('t') is not None)
        assert(test.get_by_attr('g_context') is None)
