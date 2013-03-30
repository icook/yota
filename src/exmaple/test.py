from yota import Form
from yota.nodes import *
import os
import vals
from flask import Flask, request
from flask import render_template
app = Flask(__name__)

@app.route("/")
def testing():
    count = request.args.get('count', 1)
    t = SimpleForm.get_form('test', count)
    return render_template('index.html', form=t.render())

class SimpleForm(Form):

    @classmethod
    def get_form(self, name, count=1):
        append_list = []
        for i in reversed(xrange(int(count))):
            append_list.append(
                EntryNode(title="Item {}".format(i), _attr_name='item{}'.format(i)))
        f = SimpleForm(name=name)
        f.insert_after('address', append_list)
        return f

    first = EntryNode(title="First Name")
    last = EntryNode(title="Last Name")
    address = EntryNode()
    state = ListNode(items=vals.states)
    submit = ButtonNode(title="Submit")

if __name__ == "__main__":
    app.debug = True
    app.run()
