import unittest
import sys
import yota

class TestValidation(unittest.TestCase):
    def test_min_required(self):
        class TForm(yota.Form):
            t = yota.nodes.EntryNode()
            _t_valid = yota.Check(yota.validators.MinLengthValidator(5,
                message="Darn"), 't')

        test = TForm()
        block, invalid = test._gen_validate({'t': 'short'})
        assert(len(invalid) == 0)
        block, invalid = test._gen_validate({'t': 'shor'})
        assert(len(invalid) > 0)

    def test_max_required(self):
        class TForm(yota.Form):
            t = yota.nodes.EntryNode()
            _t_valid = yota.Check(yota.validators.MaxLengthValidator(5,
                message="Darn"), 't')

        test = TForm()
        block, invalid = test._gen_validate({'t': 'shor'})
        assert(len(invalid) == 0)
        block, invalid = test._gen_validate({'t': 'toolong'})
        assert(len(invalid) > 0)

    def test_required(self):
        class TForm(yota.Form):
            t = yota.nodes.EntryNode()
            _t_valid = yota.Check(yota.validators.RequiredValidator(message="Darn"), 't')

        test = TForm()
        block, invalid = test._gen_validate({'t': 'toolong'})
        assert(len(invalid) == 0)
        block, invalid = test._gen_validate({'t': ''})
        assert(len(invalid) > 0)

    def test_error_header(self):
        class TForm(yota.Form):
            t = yota.nodes.EntryNode()
            _t_valid = yota.Check(yota.validators.RequiredValidator(message="Darn"), 't')

        test = TForm()
        invalid = test.validate_render({'t': ''},
                enable_error_header=True)
        assert(hasattr(test.start, 'error'))

class TestCheck(unittest.TestCase):
    def test_key_error_args(self):
        class TForm(yota.Form):
            t = yota.nodes.EntryNode()
            _t_valid = yota.Check(yota.validators.RequiredValidator(message="Darn"), 't')

        test = TForm()
        with self.assertRaises(yota.exceptions.FormDataAccessException):
            block, invalid = test._gen_validate({})

    def test_key_error_args(self):
        class TForm(yota.Form):
            t = yota.nodes.EntryNode()
            _t_valid = yota.Check(yota.validators.RequiredValidator(message="Darn"), target='t')

        test = TForm()
        block, invalid = test._gen_validate({'t': 'testing'})
        with self.assertRaises(yota.exceptions.FormDataAccessException):
            block, invalid = test._gen_validate({})

class TestNode(unittest.TestCase):
    def test_required(self):
        class TForm(yota.Form):
            t = yota.nodes.ListNode()

        test = TForm()
        with self.assertRaises(yota.exceptions.InvalidContextException):
            block, invalid = test.render()
if __name__ == '__main__':
    unittest.main()
