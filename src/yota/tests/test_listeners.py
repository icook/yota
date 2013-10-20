from yota import Check, Form, Listener, Blueprint
import yota.validators as validators
import yota.nodes as nodes
from yota.exceptions import *

import unittest
import yota


class TestListeners(unittest.TestCase):
    def test_basic_event(self):
        """ Canonical simple event """
        def test_func(list):
            list.data = "testing"

        class TForm(yota.Form):
            test = nodes.List()
            event = Listener("dummy", test_func, "test")
        test = TForm()
        test.trigger_event("dummy")

        assert test.test.data == "testing"

    def test_no_event(self):
        """ make sure no exception for empty events """
        test = yota.Form()
        test.trigger_event("dummy")

    def test_add_listener(self):
        """ make sure no exception for empty events """
        def test_func(list):
            list.data = "testing"

        class TForm(yota.Form):
            test = nodes.List()
        test = TForm()
        test.add_listener(Listener("dummy", test_func, "test"))
        test.trigger_event("dummy")

        assert test.test.data == "testing"


    def test_builtin_events(self):
        """  test builtin validation event calls """
        def test_func(list):
            list.data = "testing"

        class TForm(yota.Form):
            test = nodes.Entry()
            event = Listener("validate_success", test_func, "test")
        test = TForm()
        test.validate({'test': '1'})
        assert test.test.data == "testing"
        test.test.data = "something_else"

        test.validate_json({'test': '1', 'submit_action': 'true'})
        assert test.test.data == "testing"
        test.test.data = "something_else"

        test.validate_render({'test': '1'})
        assert test.test.data == "testing"
        test.test.data = "something_else"


        class TForm(yota.Form):
            test = nodes.Entry(validators=validators.MinLength(5))
            event = Listener("validate_failure", test_func, "test")
        test = TForm()
        test.validate({'test': '1'})
        assert test.test.data == "testing"
        test.test.data = "something_else"

        test.validate_json({'test': '1', 'submit_action': 'false'})
        assert test.test.data == "testing"
        test.test.data = "something_else"

        test.validate_render({'test': '1'})
        assert test.test.data == "testing"
        test.test.data = "something_else"
