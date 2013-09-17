import flask
from art17 import models
from art17 import species
from art17 import habitat
from art17 import messages
from art17.common import json_encode_more

history = flask.Blueprint('history', __name__)


@history.record
def register_handlers(state):
    app = state.app

    connect(species.comment_added, app,
            table='data_species_comments', action='add')
    connect(species.comment_edited, app,
            table='data_species_comments', action='edit')

    connect(habitat.comment_added, app,
            table='data_habitattype_comments', action='add')
    connect(habitat.comment_edited, app,
            table='data_habitattype_comments', action='edit')

    connect(messages.message_added, app,
            table='comment_messages', action='add')


def connect(signal, sender, **more_kwargs):
    @signal.connect_via(sender)
    def wrapper(sender, **kwargs):
        kwargs.update(more_kwargs)
        handle_signal(**kwargs)


def handle_signal(table, action, ob, old_data=None, **extra):
    models.db.session.flush()
    item = models.History(table=table,
                          action=action,
                          object_id=ob.id,
                          user_id=flask.g.identity.id)
    if old_data:
        item.old_data = flask.json.dumps(old_data, default=json_encode_more)
    models.db.session.add(item)


@history.route('/activitate')
def activity():
    return flask.render_template('activity.html', **{
        'history_items': iter(models.History.query),
    })
