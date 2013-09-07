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
