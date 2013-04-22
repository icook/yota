import unittest
import yota

class TestForms(unittest.TestCase):
    def test_override_start_close(self):
        class TForm(yota.Form):
            start = yota.nodes.EntryNode()
            close = yota.nodes.EntryNode()

            t = yota.nodes.EntryNode()
            _t_valid = yota.Check(yota.validators.MinLengthValidator(5,
                message="Darn"), 't')

        test = TForm()
        test.render()

    def test_dynamic_insert(self):
        class TForm(yota.Form):
            t = yota.nodes.EntryNode()
            _t_valid = yota.Check(yota.validators.MinLengthValidator(5,
                message="Darn"), 't')

        test = TForm()
        test.insert_after('t', yota.nodes.EntryNode(_attr_name='t2'))
        test.insert_after('t4', yota.nodes.EntryNode(_attr_name='t3'))

    def test_validator_shorthand(self):
        class TForm(yota.Form):
            t = yota.nodes.EntryNode(validators=yota.validators.MinLengthValidator(5,
                message="Darn"))

        test = TForm()

    def test_error_header(self):
        class TForm(yota.Form):
            t = yota.nodes.EntryNode()
            _t_valid = yota.Check(yota.validators.RequiredValidator(message="Darn"), 't')

        test = TForm()
        invalid = test.validate_render({'t': ''},
                enable_error_header=True)
        assert(hasattr(test.start, 'error'))

    def test_json_validation(self):
        class TForm(yota.Form):
            t = yota.nodes.EntryNode()
            _t_valid = yota.Check(yota.validators.RequiredValidator(message="Darn"), 't')
            t2 = yota.nodes.EntryNode()
            _t2_valid = yota.Check(yota.validators.RequiredValidator(message="Darn"), 't2')

        test = TForm()
        invalid = test.json_validate({'t': ''},
                enable_error_header=True, piecewise=True)

class TestExtra(unittest.TestCase):
    def test_get_by_attr(self):
        class TForm(yota.Form):
            t = yota.nodes.EntryNode()
            _t_valid = yota.Check(yota.validators.MinLengthValidator(5,
                message="Darn"), 't')

        test = TForm()
        assert(test.get_by_attr('t') != None)
        assert(test.get_by_attr('g_context') == None)
