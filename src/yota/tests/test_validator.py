import unittest
import yota
from yota.validators import *
from yota.nodes import *
from yota.exceptions import *


class TestValidators(unittest.TestCase):
    """ Testing for all our built-in validators """

    def run_check(self, values, validator):
        """ a utility method to run the check by hand. Pass it key value data
        like what a post object would have and it builds the args for your
        check accordingly """
        args = []
        for key, val in values.items():
            args.append(EntryNode(_attr_name=key, data=val))

        c = Check(validator, *args)
        c.resolved = True
        c()
        ret = []
        for a in args:
            if len(a.errors) > 0:
                ret.append(a)

        return ret

    def test_unicode_validator(self):
        """ make sure unicode strings don't break validators """
        for val in [MinLengthValidator(5),
                    MaxLengthValidator(5),
                    RegexValidator(regex='^[a-z]*$'),
                    RequiredValidator(),
                    EmailValidator()]:
            errors = self.run_check({'t': u"\u041f\u0440\u0438\u0432\u0435\u0442"}, val)


    def test_min_required(self):
        """ min validator testing, pos and neg """
        meth = MinLengthValidator(5, message="Darn")

        errors = self.run_check({'t':'short'}, meth)
        assert(len(errors) == 0)
        errors = self.run_check({'t':'shor'}, meth)
        assert(len(errors) > 0)

    def test_max_required(self):
        """ max validator testing, pos and neg """
        meth = MaxLengthValidator(5, message="Darn")

        errors = self.run_check({'t':'shor'}, meth)
        assert(len(errors) == 0)
        errors = self.run_check({'t':'toolong'}, meth)
        assert(len(errors) > 0)

    def test_regex_valid(self):
        """ regex validator testing, pos and neg """
        meth = RegexValidator(regex='^[a-z]*$', message='darn')

        errors = self.run_check({'t':'asdlkfdfsljgdlkfj'}, meth)
        assert(len(errors) == 0)

        # negative
        errors = self.run_check({'t':'123sdflkns'}, meth)
        assert(len(errors) > 0)

    def test_url_valid(self):
        """ regex validator testing, pos and neg """
        meth = URLValidator(message='darn')

        errors = self.run_check({'t':'http://google.com'}, meth)
        assert(len(errors) == 0)
        errors = self.run_check({'t':'http://localhost'}, meth)
        assert(len(errors) == 0)
        errors = self.run_check({'t':'http://localhost:8080/login'}, meth)
        assert(len(errors) == 0)
        errors = self.run_check({'t':'http://192.168.1.1:8080/login'}, meth)
        assert(len(errors) == 0)
        errors = self.run_check({'t':'https://192.168.1.1:8080/'}, meth)
        assert(len(errors) == 0)
        errors = self.run_check({'t':'ftp://192.168.1.1:8080/'}, meth)
        assert(len(errors) == 0)

        # negative
        errors = self.run_check({'t':'http;//google.com'}, meth)
        assert(len(errors) > 0)

    def test_email(self):
        """ email validator testing, all branches """
        meth = EmailValidator(message="Darn")

        errors = self.run_check({'t': 'm@testing.com'}, meth)
        assert(len(errors) == 0)
        errors = self.run_check({'t': 'toolong'}, meth)
        assert(len(errors) > 0)
        errors = self.run_check({'t': 'm@t%.com'}, meth)
        assert(len(errors) > 0)
        errors = self.run_check({'t': u'm@t\x80%.com'}, meth)
        assert(len(errors) > 0)
        errors = self.run_check({'t': u'@$%^%&^*m@t\x80%.com'}, meth)
        assert(len(errors) > 0)
        errors = self.run_check({'t': u'm@\xc3.com'}, meth)
        assert(len(errors) == 0)

    def test_minmax(self):
        """ minmax validator testing, pos and neg """
        meth = MinMaxValidator(2, 5, minmsg="Darn", maxmsg="Darn")

        errors = self.run_check({'t': 'ai'}, meth)
        assert(len(errors) == 0)
        errors = self.run_check({'t': 'a'}, meth)
        assert(len(errors) > 0)
        errors = self.run_check({'t': 'asdlkjdsfgljksdfg'}, meth)
        assert(len(errors) > 0)
        errors = self.run_check({'t': 'asdfg'}, meth)
        assert(len(errors) == 0)

        meth = MinMaxValidator(2, 5)
        errors = self.run_check({'t': 'aiadsflgkj'}, meth)
        assert(len(errors) > 0)
        assert("fewer" in errors[0].errors[0]['message'])

    def test_password(self):
        """ password validator testing, pos and neg """
        meth = PasswordValidator()

        errors = self.run_check({'t': 'a'}, meth)
        assert(len(errors) > 0)
        errors = self.run_check({'t': 'a&'}, meth)
        assert(len(errors) > 0)
        errors = self.run_check({'t': 'aA&'}, meth)
        assert(len(errors) > 0)
        errors = self.run_check({'t': 'aklm%klsdfg'}, meth)
        assert(len(errors) > 0)
        errors = self.run_check({'t': 'aklm% '}, meth)
        assert(len(errors) > 0)
        errors = self.run_check({'t': 'aklm%\n'}, meth)
        assert(len(errors) > 0)

        errors = self.run_check({'t': 'A7Sdfkls$gdf'}, meth)
        assert(len(errors) == 0)

    def test_username(self):
        """ username validator testing, pos and neg """
        meth = UsernameValidator()

        errors = self.run_check({'t': 'a'}, meth)
        assert(len(errors) > 0)
        errors = self.run_check({'t': 'adfgl&'}, meth)
        assert(len(errors) > 0)
        errors = self.run_check({'t': 'adfgsdfg '}, meth)
        assert(len(errors) > 0)
        errors = self.run_check({'t': 'aklm%klsdfg'}, meth)
        assert(len(errors) > 0)
        errors = self.run_check({'t': 'aklm% '}, meth)
        assert(len(errors) > 0)
        errors = self.run_check({'t': 'aklm%\n'}, meth)
        assert(len(errors) > 0)

        errors = self.run_check({'t': 'some_thing-new'}, meth)
        assert(len(errors) == 0)

    def test_integer(self):
        """ integer validator testing, pos and neg """
        meth = IntegerValidator(message="Darn")

        errors = self.run_check({'t': '12'}, meth)
        assert(len(errors) == 0)
        errors = self.run_check({'t': '12a'}, meth)
        assert(len(errors) > 0)
        errors = self.run_check({'t': 'asdfsd'}, meth)
        assert(len(errors) > 0)

    def test_matching(self):
        """ matching validator """
        meth = MatchingValidator(message="Darn")

        errors = self.run_check({'t': 'toolong', 'b': 'notmatching'}, meth)
        assert(len(errors) > 0)
        errors = self.run_check({'t': 'something', 'b': 'something'}, meth)
        assert(len(errors) == 0)

    def test_strength(self):
        """ password strength validator """
        meth = PasswordStrengthValidator(message="Darn")

        errors = self.run_check({'t': 'AA'}, meth)
        assert('1' in errors[0].errors[0]['message'])
        errors = self.run_check({'t': 'SOmething'}, meth)
        assert('2' in errors[0].errors[0]['message'])
        errors = self.run_check({'t': 'SOme33ing'}, meth)
        assert('3' in errors[0].errors[0]['message'])
        errors = self.run_check({'t': 'SOme33ing%'}, meth)
        assert('4' in errors[0].errors[0]['message'])

        meth = PasswordStrengthValidator(message="Darn",
                                         regex=["(?=.*[A-Z].*[A-Z])"])
        errors = self.run_check({'t': 'SOme33ing%'}, meth)
        assert('1' in errors[0].errors[0]['message'])

    def test_required(self):
        """ required validator """
        meth = RequiredValidator(message="Darn")

        errors = self.run_check({'t': 'toolong'}, meth)
        assert(len(errors) == 0)
        errors = self.run_check({'t': ''}, meth)
        assert(len(errors) > 0)

class TestCheck(unittest.TestCase):
    def test_key_access_exception(self):
        """ Proper raising of access exception when missing a required piece of
        data """
        class TForm(yota.Form):
            t = EntryNode()
            _t_valid = yota.Check(RequiredValidator(message="Darn"), 't')

        test = TForm()
        test.t._null_val = ['test']
        test._gen_validate({})
        assert len(test.t.data) == 1
