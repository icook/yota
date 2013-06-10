import unittest
import yota
from bs4 import BeautifulSoup
from yota.validators import *
from yota.nodes import *
from yota.exceptions import *


class TestBuiltinNodes(unittest.TestCase):
    builtin = [ListNode(items=[('1', 'some'), ('2', 'other')]),
               RadioNode(buttons=[('1', 'some'), ('2', 'other')]),
               EntryNode(),
               TextareaNode()]

    def test_radio_node(self):
        """ Test radio button for actually generating the radio buttons """
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

    def test_check_group(self):
        """ Test radio button for actually generating the radio buttons """
        class TForm(yota.Form):
            t = CheckGroupNode(boxes=[('test', '1', 'something'),
                                   ('this', '2', 'else'),
                                   ('one', '3', 'is')
                                   ])

        test = TForm(auto_start_close=False).render()
        bs = BeautifulSoup(test)
        assert(len(bs.findAll('input', {'value': '1'})) == 1)
        assert(len(bs.findAll('input', {'value': '2'})) == 1)
        assert(len(bs.findAll('input', {'value': '2'})) == 1)
        assert(len(bs.findAll('input')) == 3)

    def test_list_node(self):
        """ Tests our list node for containing input fields """
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

    def test_labels(self):
        """ Tests all applicable nodes for labels """

        for node in self.builtin:
            class TForm(yota.Form):
                t = node

            output = TForm(auto_start_close=False).render()
            bs = BeautifulSoup(output)
            print "Testing for label in " + node.__class__.__name__
            assert(len(bs.findAll('label', {'class': 'control-label'})) == 1)

    def test_entry(self):
        """ Tests our entry node for containing input fields """
        class TForm(yota.Form):
            t = EntryNode(name='something')

        test = TForm(auto_start_close=False).render()
        bs = BeautifulSoup(test)
        assert(len(bs.findAll('input', {'name': 'something'})) == 1)

    def test_textarea(self):
        """ Tests our entry node for containing input fields """
        class TForm(yota.Form):
            t = TextareaNode(rows='15', columns='20')

        test = TForm(auto_start_close=False).render()
        bs = BeautifulSoup(test)
        print bs.findAll('textarea')
        assert(len(bs.findAll('textarea', {'rows': '15', 'cols': '20'})) == 1)

    def test_submit(self):
        """ submit node for containing input fields type submit"""
        class TForm(yota.Form):
            t = SubmitNode(title='Yay')

        test = TForm(auto_start_close=False).render()
        bs = BeautifulSoup(test)
        assert(len(bs.findAll('input', {'type': 'submit', 'value': 'Yay'})) == 1)
        assert(len(bs.findAll('label')) == 0)

if __name__ == '__main__':
    unittest.main()
