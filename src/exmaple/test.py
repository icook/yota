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
    # grab our count variable from the url arguments
    count = request.args.get('count', 1)

    # Generate a regular form via a classmethod to provide extra functionality
    regular_form = SimpleForm.get_form('regular', count=count)
    ajax = SimpleForm.get_form('ajax', mode=1, count=count)
    # Handle regular submission of the form
    if request.method == 'POST' and '_ajax_' not in request.form:
        reg_render = regular_form.validate_render(request.form)
    elif '_ajax_' in request.form:
        return ajax.json_validate(request.form)
    else:
        reg_render = regular_form.render()

    # Generate our ajax form

    return render_template('index.html', reg_form=reg_render, ajax_form=ajax.render())

class SimpleForm(Form):

    @classmethod
    def get_form_from_data(cls, data):
        args = []
        for key, val in data.iteritems():
            if key.startswith('_arg_'):
                args.append(val)
        return cls.get_form(*args)

    @classmethod
    def get_form(cls, name, mode=0, count=1):

        # Make a list of nodes to add into the Form nodelist
        append_list = []
        for i in reversed(xrange(int(count))):
            append_list.append(
                EntryNode(title="Item {}".format(i), _attr_name='item{}'.format(i)))

        # Populate our global context depending on values
        g_context = {}
        if mode == 1:
            g_context['ajax'] = True

        f = SimpleForm(name=name,
                id=name,
                g_context=g_context,
                hidden={'name': name,
                        'count': count})
        f.insert_after('address', append_list)
        return f

    first = EntryNode(title="First Name", validators=MinLengthValidator(5))
    last = EntryNode(title="Last Name")
    _last_valid = Check(MinLengthValidator(5), 'last')
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
