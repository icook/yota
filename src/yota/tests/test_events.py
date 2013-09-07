import unittest
import yota
from yota.validators import *
from yota.nodes import *
from yota.exceptions import *
from copy import copy


class TestEvents(unittest.TestCase):
    def test_basic_event(self):
        """ Canonical simple event """
        def test_func(list):
            list.data = "testing"
        class TForm(yota.Form):
            test = ListNode()
            event = Event("dummy", test_func, "test")
        test = TForm()
        test.run_events("dummy")

        assert test.test.data == "testing"

    def test_no_event(self):
        """ make sure no exception for empty events """
        test = yota.Form()
        test.run_events("dummy")

    def test_builtin_events(self):
        """  test builtin validation event calls """
        def test_func(list):
            list.data = "testing"

        class TForm(yota.Form):
            test = EntryNode()
            event = Event("validate_success", test_func, "test")
        test = TForm()
        test.validate({'test': '1'})
        assert test.test.data == "testing"
        test.test.data = "something_else"

        test.json_validate({'test': '1', 'submit_action': 'true'})
        assert test.test.data == "testing"
        test.test.data = "something_else"

        test.validate_render({'test': '1'})
        assert test.test.data == "testing"
        test.test.data = "something_else"


        class TForm(yota.Form):
            test = EntryNode(validators=MinLengthValidator(5))
            event = Event("validate_failure", test_func, "test")
        test = TForm()
        test.validate({'test': '1'})
        assert test.test.data == "testing"
        test.test.data = "something_else"

        test.json_validate({'test': '1', 'submit_action': 'false'})
        assert test.test.data == "testing"
        test.test.data = "something_else"

        test.validate_render({'test': '1'})
        assert test.test.data == "testing"
        test.test.data = "something_else"
