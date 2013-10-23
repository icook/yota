from yota import Check, Form, Listener
import yota.validators as validators
import yota.nodes as nodes
from yota.exceptions import *

import unittest


class TestValidators(unittest.TestCase):
    """ Testing for all our built-in validators """

    def run_check(self, values, validator):
        """ a utility method to run the check by hand. Pass it key value data
        like what a post object would have and it builds the args for your
        check accordingly """
        args = []
        for key, val in values.items():
            args.append(nodes.Entry(_attr_name=key, data=val))

        c = Check(validator, *args)
        c.resolved = True
        c()
        ret = []
        for a in args:
            if len(a.msgs) > 0:
                ret.append(a)

        return ret

    def test_unicode_validator(self):
        """ make sure unicode strings don't break validators """
        for val in [validators.MinLength(5),
                    validators.MaxLength(5),
                    validators.Regex(regex='^[a-z]*$'),
                    validators.Required(),
                    validators.Email()]:
            msgs = self.run_check(
                {'t': u"\u041f\u0440\u0438\u0432\u0435\u0442"}, val)


    def test_min_required(self):
        """ min validator testing, pos and neg """
        meth = validators.MinLength(6, message="Darn")

        msgs = self.run_check({'t':'shorts'}, meth)
        assert(len(msgs) == 0)
        msgs = self.run_check({'t':'shor'}, meth)
        assert(len(msgs) > 0)

    def test_max_required(self):
        """ max validator testing, pos and neg """
        meth = validators.MaxLength(5, message="Darn")

        msgs = self.run_check({'t':'shor'}, meth)
        assert(len(msgs) == 0)
        msgs = self.run_check({'t':'toolong'}, meth)
        assert(len(msgs) > 0)

    def test_regex_valid(self):
        """ regex validator testing, pos and neg """
        meth = validators.Regex(regex='^[a-z]*$', message='darn')

        msgs = self.run_check({'t':'asdlkfdfsljgdlkfj'}, meth)
        assert(len(msgs) == 0)

        # negative
        msgs = self.run_check({'t':'123sdflkns'}, meth)
        assert(len(msgs) > 0)

    def test_url_valid(self):
        """ regex validator testing, pos and neg """
        meth = validators.URL(message='darn')

        msgs = self.run_check({'t':'http://google.com'}, meth)
        assert(len(msgs) == 0)
        msgs = self.run_check({'t':'http://localhost'}, meth)
        assert(len(msgs) == 0)
        msgs = self.run_check({'t':'http://localhost:8080/login'}, meth)
        assert(len(msgs) == 0)
        msgs = self.run_check({'t':'http://192.168.1.1:8080/login'}, meth)
        assert(len(msgs) == 0)
        msgs = self.run_check({'t':'https://192.168.1.1:8080/'}, meth)
        assert(len(msgs) == 0)
        msgs = self.run_check({'t':'ftp://192.168.1.1:8080/'}, meth)
        assert(len(msgs) == 0)

        # negative
        msgs = self.run_check({'t':'http;//google.com'}, meth)
        assert(len(msgs) > 0)

    def test_email(self):
        """ email validator testing, all branches """
        meth = validators.Email(message="Darn")

        msgs = self.run_check({'t': 'm@testing.com'}, meth)
        assert(len(msgs) == 0)
        msgs = self.run_check({'t': 'toolong'}, meth)
        assert(len(msgs) > 0)
        msgs = self.run_check({'t': 'm@t%.com'}, meth)
        assert(len(msgs) > 0)
        msgs = self.run_check({'t': u'm@t\x80%.com'}, meth)
        assert(len(msgs) > 0)
        msgs = self.run_check({'t': u'@$%^%&^*m@t\x80%.com'}, meth)
        assert(len(msgs) > 0)
        msgs = self.run_check({'t': u'm@\xc3.com'}, meth)
        assert(len(msgs) == 0)

    def test_minmax(self):
        """ minmax validator testing, pos and neg """
        meth = validators.MinMax(2, 5, minmsg="Darn", maxmsg="Darn")

        msgs = self.run_check({'t': 'ai'}, meth)
        assert(len(msgs) == 0)
        msgs = self.run_check({'t': 'a'}, meth)
        assert(len(msgs) > 0)
        msgs = self.run_check({'t': 'asdlkjdsfgljksdfg'}, meth)
        assert(len(msgs) > 0)
        msgs = self.run_check({'t': 'asdfg'}, meth)
        assert(len(msgs) == 0)

        meth = validators.MinMax(2, 5)
        msgs = self.run_check({'t': 'aiadsflgkj'}, meth)
        assert(len(msgs) > 0)
        assert("fewer" in msgs[0].msgs[0]['message'])

    def test_password(self):
        """ password validator testing, pos and neg """
        meth = validators.Password()

        msgs = self.run_check({'t': 'a'}, meth)
        assert(len(msgs) > 0)
        msgs = self.run_check({'t': 'a&'}, meth)
        assert(len(msgs) > 0)
        msgs = self.run_check({'t': 'aA&'}, meth)
        assert(len(msgs) > 0)
        msgs = self.run_check({'t': 'aklm%klsdfg'}, meth)
        assert(len(msgs) > 0)
        msgs = self.run_check({'t': 'aklm% '}, meth)
        assert(len(msgs) > 0)
        msgs = self.run_check({'t': 'aklm%\n'}, meth)
        assert(len(msgs) > 0)

        msgs = self.run_check({'t': 'A7Sdfkls$gdf'}, meth)
        assert(len(msgs) == 0)

    def test_username(self):
        """ username validator testing, pos and neg """
        meth = validators.Username()

        msgs = self.run_check({'t': 'a'}, meth)
        assert(len(msgs) > 0)
        msgs = self.run_check({'t': 'adfgl&'}, meth)
        assert(len(msgs) > 0)
        msgs = self.run_check({'t': 'adfgsdfg '}, meth)
        assert(len(msgs) > 0)
        msgs = self.run_check({'t': 'aklm%klsdfg'}, meth)
        assert(len(msgs) > 0)
        msgs = self.run_check({'t': 'aklm% '}, meth)
        assert(len(msgs) > 0)
        msgs = self.run_check({'t': 'aklm%\n'}, meth)
        assert(len(msgs) > 0)

        msgs = self.run_check({'t': 'some_thing-new'}, meth)
        assert(len(msgs) == 0)

    def test_integer(self):
        """ integer validator testing, pos and neg """
        meth = validators.Integer(message="Darn")

        msgs = self.run_check({'t': '12'}, meth)
        assert(len(msgs) == 0)
        msgs = self.run_check({'t': '12a'}, meth)
        assert(len(msgs) > 0)
        msgs = self.run_check({'t': 'asdfsd'}, meth)
        assert(len(msgs) > 0)

    def test_matching(self):
        """ matching validator """
        meth = validators.Matching(message="Darn")

        msgs = self.run_check({'t': 'toolong', 'b': 'notmatching'}, meth)
        assert(len(msgs) > 0)
        msgs = self.run_check({'t': 'something', 'b': 'something'}, meth)
        assert(len(msgs) == 0)

    def test_strength(self):
        """ password strength validator """
        meth = validators.PasswordStrength(message="Darn")

        msgs = self.run_check({'t': 'AA'}, meth)
        assert('1' in msgs[0].msgs[0]['message'])
        msgs = self.run_check({'t': 'SOmething'}, meth)
        assert('2' in msgs[0].msgs[0]['message'])
        msgs = self.run_check({'t': 'SOme33ing'}, meth)
        assert('3' in msgs[0].msgs[0]['message'])
        msgs = self.run_check({'t': 'SOme33ing%'}, meth)
        assert('4' in msgs[0].msgs[0]['message'])

        meth = validators.PasswordStrength(message="Darn",
                                         regex=["(?=.*[A-Z].*[A-Z])"])
        msgs = self.run_check({'t': 'SOme33ing%'}, meth)
        assert('1' in msgs[0].msgs[0]['message'])

    def test_required(self):
        """ required validator """
        meth = validators.Required(message="Darn")

        msgs = self.run_check({'t': 'toolong'}, meth)
        assert(len(msgs) == 0)
        msgs = self.run_check({'t': ''}, meth)
        assert(len(msgs) > 0)

class TestCheck(unittest.TestCase):
    def test_key_access_exception(self):
        """ Proper raising of access exception when missing a required piece of
        data """
        class TForm(Form):
            t = nodes.Entry()
            _t_valid = Check(validators.Required(message="Darn"), 't')

        test = TForm()
        test.t._null_val = ['test']
        test._gen_validate({})
        assert len(test.t.data) == 1
