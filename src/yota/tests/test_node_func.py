import unittest
import yota
from bs4 import BeautifulSoup
from yota.validators import *
from yota.nodes import *
from yota.exceptions import *


class TestBuiltinNodes(unittest.TestCase):
    def test_radio_node(self):
        class TForm(yota.Form):
            t = RadioNode(buttons=[('1', 'something'),
                                   ('2', 'else'),
                                   ('3', 'is')
                                   ])

        test = TForm(auto_start_close=False).render()
        bs = BeautifulSoup(test)
        assert(len(bs.findAll('input', {'value': '1'})) == 1)
        assert(len(bs.findAll('input', {'value': '2'})) == 1)
        assert(len(bs.findAll('input', {'value': '2'})) == 1)
        assert(len(bs.findAll('input')) == 3)

    def test_list_node(self):
        class TForm(yota.Form):
            t = ListNode(items=[('1', 'something'),
                                ('2', 'else'),
                                ('3', 'is')
                                ])

        test = TForm(auto_start_close=False).render()
        bs = BeautifulSoup(test)
        assert(len(bs.findAll('option', {'value': '1'})) == 1)
        assert(len(bs.findAll('option', {'value': '2'})) == 1)
        assert(len(bs.findAll('option', {'value': '2'})) == 1)
        assert(len(bs.findAll('option')) == 3)

if __name__ == '__main__':
    unittest.main()
