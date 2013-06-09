import unittest
import yota
from yota.validators import *
from yota.nodes import *


class TestValidation(unittest.TestCase):
    def test_min_required(self):
        class TForm(yota.Form):
            t = EntryNode()
            _t_valid = yota.Check(
                MinLengthValidator(5, message="Darn"), 't')

        test = TForm()
        block, invalid = test._gen_validate({'t': 'short'})
        assert(len(invalid) == 0)
        block, invalid = test._gen_validate({'t': 'shor'})
        assert(len(invalid) > 0)

    def test_max_required(self):
        class TForm(yota.Form):
            t = EntryNode()
            _t_valid = yota.Check(
                MaxLengthValidator(5, message="Darn"), 't')

        test = TForm()
        block, invalid = test._gen_validate({'t': 'shor'})
        assert(len(invalid) == 0)
        block, invalid = test._gen_validate({'t': 'toolong'})
        assert(len(invalid) > 0)

    def test_email(self):
        class TForm(yota.Form):
            t = EntryNode()
            _t_valid = yota.Check(EmailValidator(
                message="Darn"), 't')

        test = TForm()
        block, invalid = test._gen_validate({'t': 'm@testing.com'})
        assert(len(invalid) == 0)
        block, invalid = test._gen_validate({'t': 'toolong'})
        assert(len(invalid) > 0)
        block, invalid = test._gen_validate({'t': 'm@t%.com'})
        assert(len(invalid) > 0)
        block, invalid = test._gen_validate({'t': u'm@t\x80%.com'})
        assert(len(invalid) > 0)
        block, invalid = test._gen_validate({'t': u'm@\xc3.com'})
        assert(len(invalid) == 0)

    def test_required(self):
        class TForm(yota.Form):
            t = EntryNode()
            _t_valid = yota.Check(RequiredValidator(message="Darn"), 't')

        test = TForm()
        block, invalid = test._gen_validate({'t': 'toolong'})
        assert(len(invalid) == 0)
        block, invalid = test._gen_validate({'t': ''})
        assert(len(invalid) > 0)

    def test_non_blocking(self):
        class TForm(yota.Form):
            t = EntryNode()
            _t_valid = yota.Check(
                NonBlockingDummyValidator(), 't')

        test = TForm()
        block, invalid = test._gen_validate({'t': 'toolong'})
        assert(block is False)


class TestCheck(unittest.TestCase):
    def test_key_error_args(self):
        class TForm(yota.Form):
            t = EntryNode()
            _t_valid = yota.Check(
                RequiredValidator(message="Darn"), 't')

        test = TForm()
        self.assertRaises(yota.exceptions.DataAccessException,
                          test._gen_validate, {})

    def test_key_error(self):
        class TForm(yota.Form):
            t = EntryNode()
            _t_valid = yota.Check(
                RequiredValidator(message="Darn"), target='t')

        test = TForm()
        block, invalid = test._gen_validate({'t': 'testing'})
        assert(test.t.data == 'testing')


class TestNode(unittest.TestCase):
    def test_required(self):
        class TForm(yota.Form):
            t = ListNode()

        test = TForm()
        self.assertRaises(yota.exceptions.InvalidContextException, test.render)


if __name__ == '__main__':
    unittest.main()
