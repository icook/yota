from yota import Form
from yota.nodes import *

class SimpleForm(Form):

    def __init__(self):
        super(SimpleForm, self).__init__()

    submit = ButtonNode()
    okay = ButtonNode()
    persons = ListNode()

def main():
    t = SimpleForm()
    print t.render()

if __name__ == "__main__":
    main()
