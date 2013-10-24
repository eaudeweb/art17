# encoding: utf-8

from datetime import datetime
import flask
from flask.ext.principal import Permission
from blinker import Signal
from art17 import models
from art17.auth import require, need

replies = flask.Blueprint('replies', __name__)

reply_added = Signal()
reply_removed = Signal()


def _get_comment_or_404(comment_id):
    for cls in [models.DataSpeciesComment,
                models.DataHabitattypeComment]:
        comment = cls.query.get(comment_id)
        if comment is not None:
            return comment

    else:
        flask.abort(404)


def _dump_reply_data(reply):
    return {k: getattr(reply, k)
            for k in ['text', 'user_id', 'parent', 'date']}


@replies.route('/replici/<comment_id>/nou', methods=['POST'])
@require(Permission(need.authenticated))
def new(comment_id):
    comment = _get_comment_or_404(comment_id)

    if flask.request.method == 'POST':
        reply = models.CommentReply(
            text=flask.request.form['text'],
            user_id=flask.g.identity.id,
            date=datetime.utcnow(),
            parent=comment.id)
        models.db.session.add(reply)
        app = flask.current_app._get_current_object()
        reply_added.send(app, ob=reply,
                           new_data=_dump_reply_data(reply))
        models.db.session.commit()
        url = flask.url_for('.index', comment_id=comment_id)
        return flask.redirect(url)

    return flask.render_template('replies/new.html')


@replies.route('/replici/sterge', methods=['POST'])
@require(Permission(need.admin))
def remove():
    reply_id = flask.request.args['reply_id']
    next_url = flask.request.args['next']
    reply = models.CommentReply.query.get_or_404(reply_id)
    user_id = reply.user_id
    models.db.session.delete(reply)
    app = flask.current_app._get_current_object()
    reply_removed.send(app, ob=reply, old_data=_dump_reply_data(reply))
    models.db.session.commit()
    flask.flash(u"Replica lui %s a fost ștearsă." % user_id, 'success')
    return flask.redirect(next_url)


@replies.route('/replici/citit', methods=['POST'])
@require(Permission(need.authenticated))
def set_read_status():
    reply_id = flask.request.form['reply_id']
    read = (flask.request.form.get('read') == 'on')
    reply = models.CommentReply.query.get_or_404(reply_id)

    user_id = flask.g.identity.id
    if user_id is None:
        flask.abort(403)

    existing = (models.CommentReplyRead
                    .query.filter_by(reply_id=reply.id, user_id=user_id))

    if read:
        if not existing.count():
            row = models.CommentReplyRead(reply_id=reply.id, user_id=user_id)
            models.db.session.add(row)
            models.db.session.commit()

    else:
        existing.delete()
        models.db.session.commit()

    return flask.jsonify(read=read)


@replies.route('/replici/<comment_id>')
def index(comment_id):
    replies = (models.CommentReply
                    .query.filter_by(parent=comment_id).all())
    user_id = flask.g.identity.id

    if user_id:
        read_by_user = (models.CommentReplyRead
                            .query.filter_by(user_id=user_id))
        read_msgs = set(r.reply_id for r in read_by_user)

    else:
        read_msgs = []

    return flask.render_template('replies/index.html', **{
        'comment_id': comment_id,
        'replies': replies,
        'read_msgs': read_msgs,
        'can_post_new_reply': Permission(need.authenticated).can(),
        'can_set_read_status': Permission(need.authenticated).can(),
        'can_delete_reply': Permission(need.admin).can()
    })