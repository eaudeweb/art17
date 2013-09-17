# encoding: utf-8

from datetime import datetime
import flask
from blinker import Signal
from art17 import models
from art17.auth import admin_permission

messages = flask.Blueprint('messages', __name__)

message_added = Signal()
message_removed = Signal()


def _get_comment_or_404(comment_id):
    for cls in [models.DataSpeciesComment, models.DataHabitattypeComment]:
        comment = cls.query.get(comment_id)
        if comment is not None:
            return comment

    else:
        flask.abort(404)


@messages.route('/mesaje/<comment_id>/nou', methods=['GET', 'POST'])
def new(comment_id):
    comment = _get_comment_or_404(comment_id)

    if flask.request.method == 'POST':
        message = models.CommentMessage(
            text=flask.request.form['text'],
            user_id=flask.g.identity.id,
            date=datetime.utcnow(),
            parent=comment.id)
        models.db.session.add(message)
        app = flask.current_app._get_current_object()
        message_added.send(app, ob=message)
        models.db.session.commit()
        return flask.redirect(flask.url_for('.index', comment_id=comment_id))

    return flask.render_template('messages/new.html')


@messages.route('/mesaje/sterge', methods=['POST'])
@admin_permission.require(403)
def remove():
    message_id = flask.request.args['message_id']
    next_url = flask.request.args['next']
    message = models.CommentMessage.query.get_or_404(message_id)
    user_id = message.user_id
    models.db.session.delete(message)
    app = flask.current_app._get_current_object()
    old_data = {k: getattr(message, k)
                for k in ['text', 'user_id', 'parent', 'date']}
    message_removed.send(app, ob=message, old_data=old_data)
    models.db.session.commit()
    flask.flash(u"Mesajul lui %s a fost șters." % user_id, 'success')
    return flask.redirect(next_url)


@messages.route('/mesaje/citit', methods=['POST'])
def set_read_status():
    message_id = flask.request.form['message_id']
    read = (flask.request.form.get('read') == 'on')
    message = models.CommentMessage.query.get_or_404(message_id)

    user_id = flask.g.identity.id
    if user_id is None:
        flask.abort(403)

    existing = (models.CommentMessageRead.query
                                         .filter_by(message_id=message.id,
                                                    user_id=user_id))

    if read:
        if not existing.count():
            row = models.CommentMessageRead(message_id=message.id,
                                            user_id=user_id)
            models.db.session.add(row)
            models.db.session.commit()

    else:
        existing.delete()
        models.db.session.commit()

    return flask.jsonify(read=read)


@messages.route('/mesaje/<comment_id>')
def index(comment_id):
    messages = models.CommentMessage.query.filter_by(parent=comment_id).all()
    user_id = flask.g.identity.id

    if user_id:
        read_by_user = (models.CommentMessageRead.query
                                                 .filter_by(user_id=user_id))
        read_msgs = set(r.message_id for r in read_by_user)

    else:
        read_msgs = []

    return flask.render_template('messages/index.html', **{
        'comment_id': comment_id,
        'messages': messages,
        'read_msgs': read_msgs,
    })
