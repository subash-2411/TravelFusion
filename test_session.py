import flask

app = flask.Flask(__name__)
app.secret_key = 'test'

@app.route('/')
def index():
    flask.session['test'] = True
    return flask.render_template_string('{% if session.pop("test", False) %}Yes{% else %}No{% endif %}')

with app.test_request_context('/'):
    res = app.test_client().get('/')
    print("Result:", res.data.decode())
