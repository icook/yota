import unittest
import yota
from yota.validators import *
from yota.nodes import *
from yota.exceptions import *


class TestValidators(unittest.TestCase):
    """ Testing for all our built-in validators """

    def test_min_required(self):
        """ The min validator testing, pos and neg """
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
        """ The max validator testing, pos and neg """
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
        """ The email validator testing, all branches """
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
        block, invalid = test._gen_validate({'t': u'@$%^%&^*m@t\x80%.com'})
        assert(len(invalid) > 0)
        block, invalid = test._gen_validate({'t': u'm@\xc3.com'})
        assert(len(invalid) == 0)

    def test_required(self):
        """ Required validator """
        class TForm(yota.Form):
            t = EntryNode()
            _t_valid = yota.Check(RequiredValidator(message="Darn"), 't')

        test = TForm()
        block, invalid = test._gen_validate({'t': 'toolong'})
        assert(len(invalid) == 0)
        block, invalid = test._gen_validate({'t': ''})
        assert(len(invalid) > 0)

    def test_non_blocking(self):
        """ Ensure that a non-blocking validators validation is successful """
        class TForm(yota.Form):
            t = EntryNode()
            _t_valid = yota.Check(
                NonBlockingDummyValidator(), 't')

        test = TForm()
        block, invalid = test._gen_validate({'t': 'toolong'})
        assert(block is False)


class TestCheck(unittest.TestCase):
    def test_key_access_exception(self):
        """ Proper raising of access exception when missing a required piece of
        data """
        class TForm(yota.Form):
            t = EntryNode()
            _t_valid = yota.Check(
                RequiredValidator(message="Darn"), 't')

        test = TForm()
        self.assertRaises(DataAccessException,
                          test._gen_validate, {})

    def test_data_resolver(self):
        """ Simple test for default data resolution implemented by Check """
        class TForm(yota.Form):
            t = EntryNode()
            _t_valid = yota.Check(
                RequiredValidator(message="Darn"), target='t')

        test = TForm()
        block, invalid = test._gen_validate({'t': 'testing'})
        assert(test.t.data == 'testing')


if __name__ == '__main__':
    unittest.main()
