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

    def test_textarea(self):
        """ Tests our textarea node for containing fields and content"""
        class TForm(yota.Form):
            t = TextareaNode(rows='15', columns='20')

        test = TForm(auto_start_close=False).render()
        bs = BeautifulSoup(test)
        assert(len(bs.findAll('textarea', {'rows': '15', 'cols': '20'})) == 1)

        class TForm(yota.Form):
            t = TextareaNode(rows='15', columns='20')
            _t_long = Check(MinLengthValidator(5), 't')
        test = TForm(auto_start_close=False).validate_render({'t': 'test'})
        bs = BeautifulSoup(test)
        assert('test' in bs.findAll('textarea')[0].contents[0].strip())

if __name__ == '__main__':
    unittest.main()
