import unittest
import yota
from bs4 import BeautifulSoup
from yota.validators import *
from yota.nodes import *
from yota.exceptions import *


class TestBuiltinNodes(unittest.TestCase):
    """ Some functional testing for our builtin nodes. Still very incomplete """
    builtin = [ListNode(items=[('1', 'some'), ('2', 'other')]),
               RadioNode(buttons=[('1', 'some'), ('2', 'other')]),
               EntryNode(),
               TextareaNode()]

    def test_radio_node(self):
        """ radio node generating the radio buttons """
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

    def test_check_node(self):
        """ check box node for generating check box """
        class TForm(yota.Form):
            t = CheckNode(name='test')

        test = TForm(auto_start_close=False).render()
        bs = BeautifulSoup(test)
        assert(len(bs.findAll('input', {'name': 'test'})) == 1)
        assert(len(bs.findAll('input', {'type': 'checkbox'})) == 1)
        assert(len(bs.findAll('input')) == 1)

    def test_check_group(self):
        """ grouped checkboxes generating check boxes """
        class TForm(yota.Form):
            t = CheckGroupNode(boxes=[('test', 'something'),
                                   ('this', 'else'),
                                   ('one', 'is')
                                   ])

        test = TForm(auto_start_close=False).render()
        bs = BeautifulSoup(test)
        assert(len(bs.findAll('input', {'name': 'test'})) == 1)
        assert(len(bs.findAll('input', {'name': 'this'})) == 1)
        assert(len(bs.findAll('input', {'name': 'one'})) == 1)
        assert(len(bs.findAll('input')) == 3)

    def test_list_node(self):
        """ list node contains input fields """
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
        """ all builtin nodes have labels """

        for node in self.builtin:
            class TForm(yota.Form):
                t = node

            output = TForm(auto_start_close=False).render()
            bs = BeautifulSoup(output)
            print "Testing for label in " + node.__class__.__name__
            assert(len(bs.findAll('label', {'class': 'control-label'})) == 1)

    def test_entry(self):
        """ entry node contains input field """
        class TForm(yota.Form):
            t = EntryNode(name='something')

        test = TForm(auto_start_close=False).render()
        bs = BeautifulSoup(test)
        assert(len(bs.findAll('input', {'name': 'something'})) == 1)

    def test_textarea(self):
        """ textarea contains textarea field """
        class TForm(yota.Form):
            t = TextareaNode(rows='15', columns='20')

        test = TForm(auto_start_close=False).render()
        bs = BeautifulSoup(test)
        assert(len(bs.findAll('textarea', {'rows': '15', 'cols': '20'})) == 1)

    def test_submit(self):
        """ submit node for containing input fields type submit """
        class TForm(yota.Form):
            t = SubmitNode(title='Yay')

        test = TForm(auto_start_close=False).render()
        bs = BeautifulSoup(test)
        assert(len(bs.findAll('input', {'type': 'submit', 'value': 'Yay'})) == 1)
        assert(len(bs.findAll('label')) == 0)

    def test_textarea_content(self):
        """ textarea data gets passed back in correctly """
        class TForm(yota.Form):
            t = TextareaNode(rows='15', columns='20')
            _t_long = Check(MinLengthValidator(5), 't')
        success, test = TForm(auto_start_close=False).validate_render({'t': 'test'})
        bs = BeautifulSoup(test)
        assert('test' in bs.findAll('textarea')[0].contents[0].strip())

if __name__ == '__main__':
    unittest.main()
