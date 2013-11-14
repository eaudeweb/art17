# encoding: utf-8

import flask
from flask.ext.mail import Mail, Message
from art17 import species
from art17 import replies
from art17 import habitat
from art17 import models

notifications = flask.Blueprint('notifications', __name__)
mail = Mail()


@notifications.record
def register_handlers(state):
    app = state.app
    mail.init_app(app)

    connect(species.comment_added, app,
            table='data_species_regions', action='add')
    connect(species.comment_edited, app,
            table='data_species_regions', action='edit')
    connect(species.comment_status_changed, app,
            table='data_species_regions', action='status')
    connect(species.comment_deleted, app,
            table='data_species_regions', action='delete')

    connect(habitat.comment_added, app,
            table='data_habitattype_regions', action='add')
    connect(habitat.comment_edited, app,
            table='data_habitattype_regions', action='edit')
    connect(habitat.comment_status_changed, app,
            table='data_habitattype_regions', action='status')
    connect(habitat.comment_deleted, app,
            table='data_habitattype_regions', action='delete')

    connect(replies.reply_added, app,
            table='comment_replies', action='add')
    #connect(replies.reply_removed, app,
    #        table='comment_replies', action='remove')


def connect(signal, sender, **more_kwargs):
    @signal.connect_via(sender)
    def wrapper(sender, **kwargs):
        kwargs.update(more_kwargs)
        handle_signal(**kwargs)


def handle_signal(table, action, ob, **extra):
    if not ob.id:
        models.db.session.flush()
        assert ob.id

    recipients = get_notification_emails(ob)
    for r in recipients:
        msg = Message(body=create_message(table, action, ob, r),
                subject='Notificare',
                recipients=[r.email]
        )
        mail.send(msg)


def create_message(table, action, ob, user):
    tpl = 'unknown.html'
    if table == 'data_species_regions':
        tpl = 'notifications/species.html'
    elif table == 'data_habitattype_regions':
        tpl = 'notifications/habitat.html'
    elif table == 'comment_replies':
        tpl = 'notifications/comment.html'
    return flask.render_template(tpl, **{'object': ob, 'user': user, 'action': action})


@notifications.app_template_global('resource_url')
def resource_url(table, objectid, _external=False):
    obj = get_parent_object(table, objectid)
    if table == 'species':
        return flask.url_for('species.index', _external=_external) + '?species=' + str(obj.species.code)
    if table == 'habitat':
        return flask.url_for('habitat.index', _external=_external) + '?habitat=' + str(obj.habitat.code)
    return ''


def get_parent_object(table, objectid):
    if table == 'species':
        return models.DataSpeciesRegion.query.get(objectid)
    if table == 'habitat':
        return models.DataHabitattypeRegion.query.get(objectid)
    return None


def get_notification_emails(obj):
    if isinstance(obj, models.CommentReply):
        parent = get_parent_object(obj.parent_table, obj.parent_id)
        identifier = parent.identifier
    else:
        identifier = obj.identifier
    # TODO: get emails from SharePoint, using identity
    return models.NotificationUser.query.all()