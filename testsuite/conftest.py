import sys
from path import path
import pytest
from mock import Mock

sys.path.append(path(__file__).abspath().parent.parent)


@pytest.fixture
def species_app():
    import flask
    from art17.species import species
    app = flask.Flask('art17.app')
    app.config['TESTING'] = True
    app.register_blueprint(species)
    @app.before_request
    def set_identity():
        flask.g.identity = Mock(id='somewho')
    from art17.models import db
    db.init_app(app)
    with app.app_context():
        db.create_all()
    return app


@pytest.fixture
def habitat_app():
    import flask
    from art17.habitat import habitat
    app = flask.Flask('art17.app')
    app.config['TESTING'] = True
    app.register_blueprint(habitat)
    @app.before_request
    def set_identity():
        flask.g.identity = Mock(id='somewho')
    from art17.models import db
    db.init_app(app)
    with app.app_context():
        db.create_all()
    return app
