import flask
from flask.ext.script import Manager
from path import path

views = flask.Blueprint('views', __name__)


@views.route('/')
def home():
    return flask.render_template('home.html')


@views.app_url_defaults
def bust_cache(endpoint, values):
    if endpoint == 'static':
        filename = values['filename']
        file_path = path(flask.current_app.static_folder) / filename
        if file_path.exists():
            mtime = file_path.stat().st_mtime
            key = ('%x' % mtime)[-6:]
            values['t'] = key


def create_app():
    from art17.common import common
    from art17.species import species
    from art17.habitat import habitat
    from art17 import models

    app = flask.Flask(__name__, instance_relative_config=True)
    app.jinja_options['extensions'].append('jinja2.ext.do')
    app.config.from_pyfile('settings.py', silent=True)
    app.register_blueprint(views)
    app.register_blueprint(common)
    app.register_blueprint(species)
    app.register_blueprint(habitat)
    models.db.init_app(app)

    return app


manager = Manager(create_app)


if __name__ == '__main__':
    manager.run()
