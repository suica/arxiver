import os

from flask import Flask
from flask_migrate import Migrate

from apis import init_api
from models import init_db, db
from pages import init_page


def init_csrf_protection(app):
    from flask_wtf.csrf import CSRFProtect
    CSRFProtect(app)


class CustomFlask(Flask):
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update(dict(
        variable_start_string='{{{',  # I'm changing this because Vue.js uses '{{' / '}}'
        variable_end_string='}}}',
    ))


app = CustomFlask(__name__)

migrate = Migrate(app, db)

if __name__ == '__main__':
    with app.app_context():
        init_db(app)
    init_api(app)
    init_page(app)
    app.run(debug=True,host='0.0.0.0',port=5000)
