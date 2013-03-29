from yota import Form
from yota.nodes import *
from flask import Flask
from flask import render_template
app = Flask(__name__)

@app.route("/")
def testing():
    t = SimpleForm.get_form('test')
    return render_template('index.html', form=t.render())

class SimpleForm(Form):

    @classmethod
    def get_form(self, name):
        return SimpleForm(name=name)

    submit = ButtonNode(title="Submit")
    okay = ButtonNode(title="Okay")
    persons = ListNode(items=[("test", "that"),("test1", "those")])

if __name__ == "__main__":
    app.run()
