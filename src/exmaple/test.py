from yota import Form
from yota.nodes import *
from yota.validators import Check, MinLengthValidator, RequiredValidator
import os
import vals
from flask import Flask, request
from flask import render_template
app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def testing():
    count = request.args.get('count', 1)
    t = SimpleForm.get_form('test', count)
    if request.method == 'POST':
        frm = t.validate_render(request.form)
    else:
        frm = t.render()
    return render_template('index.html', form=frm)

@app.route("/json", methods=['POST'])
def json_validate():
    if request.method == 'POST':
        # extract our parameters that were used to generate the form from the
        # hidden fields that were generated in the begin element
        t = SimpleForm.get_form_from_data(request.form)
        json = t.json_validate(request.form)
        return json

class BaseNode(Node):
    base = "horiz.html"

class ListNode(BaseNode):
    template = 'list.html'
    _requires = ['items']

class ButtonNode(BaseNode):
    template = 'button.html'

class EntryNode(BaseNode):
    template = 'entry.html'

class SubmitNode(BaseNode):
    template = 'submit.html'

class SimpleForm(Form):
    g_context = {'ajax': True}

    @classmethod
    def get_form_from_data(cls, data):
        args = []
        for key, val in data.iteritems():
            if key.startswith('_arg_'):
                args.append(val)
        return cls.get_form(*args)

    @classmethod
    def get_form(cls, name, count=1):
        append_list = []
        for i in reversed(xrange(int(count))):
            append_list.append(
                EntryNode(title="Item {}".format(i), _attr_name='item{}'.format(i)))
        f = SimpleForm(name=name, id=name, ajax=True, hidden={'name': name, 'count': count})
        f.insert_after('address', append_list)
        return f

    first = EntryNode(title="First Name", validators=MinLengthValidator(5))
    last = EntryNode(title="Last Name")
    _last_valid = Check(MinLengthValidator(5), 'last')
    #_email_valid = Validator(PasswordSameValidator(), 'email', ['email', 'email_confirm'], {'test': 'first'})
    address = EntryNode(validators=RequiredValidator())
    state = ListNode(items=vals.states)
    submit = SubmitNode(title="Submit")

    def process_validation(self, vdict):
        if 'message' not in vdict:
            vdict['message'] = 'Please enter a valid value.'
        return vdict

if __name__ == "__main__":
    app.debug = True
    app.run()
