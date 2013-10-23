# encoding: utf-8

import re
from datetime import datetime
from dateutil import tz
from decimal import Decimal
import urllib
from babel.dates import format_datetime
from jinja2 import evalcontextfilter, Markup, escape
import flask
import flask.views
from flask.ext.principal import Permission, Denial
from werkzeug.datastructures import MultiDict
from sqlalchemy import func
from art17 import models
from art17.auth import need
import lookup


DATE_FORMAT = {
    'day': u'd\u00a0MMM',
    'long': u'd\u00a0MMMM\u00a0y\u00a0HH:mm',
}

_paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')

STATUS_OPTIONS = [
    ('new',         u"-- neevaluat"),
    ('investigate', u"!! necesită mai multe investigații"),
    ('incomplete',  u"CO necesită completări/corecții"),
    ('approved',    u"OK propus pentru păstrare"),
    ('rejected',    u"REJ refuzat, motive în replică"),
    ('invalid',     u"NO invalid"),
    ('question',    u"?? discutabil"),
    ('final',       u"FIN raport modificat în urma consultării"),
]

STATUS_VALUES = list(dict(STATUS_OPTIONS))

APPROVED_STATUS = 'approved'
assert APPROVED_STATUS in STATUS_VALUES

CONCLUSION_COLOR = {
    'FV': '71A057',
    'U1': 'E7E737',
    'U2': 'F76C27',
    'XX': 'FFFFFF',
}


def perm_create_comment(record):
    return Permission(need.authenticated)


def perm_edit_comment(comment):
    if comment.user_id:
        return Permission(need.admin, need.user_id(comment.user_id))
    else:
        return Permission(need.admin)


def perm_update_comment_status(comment):
    return Permission(need.admin)


def perm_delete_comment(comment):
    if comment.status == APPROVED_STATUS:
        return Denial(need.everybody)
    elif comment.user_id:
        return Permission(need.admin, need.user_id(comment.user_id))
    else:
        return Permission(need.admin)


common = flask.Blueprint('common', __name__)


@common.app_context_processor
def inject_permissions():
    return {
        'perm_create_comment': perm_create_comment,
        'perm_edit_comment': perm_edit_comment,
        'perm_update_comment_status': perm_update_comment_status,
        'perm_delete_comment': perm_delete_comment,
    }


@common.app_context_processor
def inject_constants():
    return {'TREND_NAME': lookup.TREND_NAME,
            'METHODS_USED': lookup.METHODS_USED,
            'LU_FV_RANGE_OP': lookup.LU_FV_RANGE_OP,
            'LU_FV_RANGE_OP_FUNCT': lookup.LU_FV_RANGE_OP_FUNCT,
            'LU_POP_NUMBER': lookup.LU_POP_NUMBER,
            'CONCLUSIONS': lookup.CONCLUSIONS,
            'LU_REASONS_FOR_CHANGE': lookup.LU_REASONS_FOR_CHANGE,
            'QUALITY': lookup.QUALITY,
            'STATUS_OPTIONS': STATUS_OPTIONS}


@common.app_template_filter('local_date')
def local_date(value, format='day'):
    if not value:
        return ''
    utc = tz.gettz('UTC')
    local_tz = tz.gettz('Europe/Bucharest')
    local_value = value.replace(tzinfo=utc).astimezone(local_tz)
    return format_datetime(local_value, DATE_FORMAT[format], locale='ro')


@common.app_template_filter('nl2br')
@evalcontextfilter
def nl2br(eval_ctx, value):
    result = u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', '<br>\n') \
        for p in _paragraph_re.split(escape(value)))
    if eval_ctx.autoescape:
        result = Markup(result)
    return result


def flatten_dict(data):
    rv = {}
    for k, v in data.items():
        if isinstance(v, dict):
            for kx, vx in flatten_dict(v).items():
                rv[k + '.' + kx] = vx
        else:
            rv[k] = '' if v is None else unicode(v)
    return rv


def json_encode_more(value):
    if isinstance(value, Decimal):
        return float(value)

    if isinstance(value, datetime):
        return value.isoformat()

    raise TypeError


class IndexView(flask.views.View):

    def parse_request(self):
        self.subject_code = flask.request.args.get(self.subject_name)

        if self.subject_code:
            self.subject = (self.subject_cls.query
                        .filter_by(code=self.subject_code)
                        .join(models.DataSpecies.lu)
                        .first_or_404())
        else:
            self.subject = None

        self.region_code = flask.request.args.get('region', '')
        if self.region_code:
            self.region = (models.LuBiogeoreg.query
                        .filter_by(code=self.region_code)
                        .first_or_404())
        else:
            self.region = None

        if self.subject:
            self.records = self.subject.regions
            self.comments = (self.subject.comments
                                            .filter_by(deleted=False))

            if self.region:
                self.records = self.records.filter_by(region=self.region.code)
                self.comments = self.comments.filter_by(
                                        region=self.region.code)

            CommentReply = models.CommentReply
            self.message_counts = dict(models.db.session.query(
                                    CommentReply.parent,
                                    func.count(CommentReply.id)
                                ).group_by(CommentReply.parent))

        self.subject_list = (self.subject_cls.query
                            .join(self.record_cls)
                            .order_by(self.subject_cls.code))

    def get_pressures(self, record):
        return record.pressures.all()

    def prepare_context(self):
        self.ctx.update({
            'subject_list': self.get_subject_list(),
            'current_subject_code': self.subject_code,
            'current_region_code': self.region_code,
            'conclusion_next': self.get_comment_next_url(),
            'blueprint': self.blueprint,
        })

        if self.subject:
            map_colors = [{
                    'region': r.region,
                    'code': CONCLUSION_COLOR.get(r.conclusion_assessment),
                } for r in self.records]
            self.ctx.update({
                'code': self.subject.code,
                'name': self.subject.lu.display_name,
                'records': [self.parse_record(r) for r in self.records],
                'comments': [self.parse_record(r, is_conclusion=True)
                             for r in self.comments],
                'message_counts': self.message_counts,
                'map_url': self.map_url_template.format(**{
                        self.subject_name: self.subject.code,
                        'regions': urllib.quote(flask.json.dumps(map_colors)),
                    })
            })

    def dispatch_request(self):
        self.parse_request()
        self.ctx = {}
        self.prepare_context()
        return flask.render_template(self.template, **self.ctx)


class CommentView(flask.views.View):

    methods = ['GET', 'POST']

    def dispatch_request(self, record_id=None, conclusion_id=None):
        if record_id:
            new_conclusion = True
            self.record = self.record_cls.query.get_or_404(record_id)
            perm_create_comment(self.record).test()
            self.conclusion = self.comment_cls(user_id=flask.g.identity.id,
                                            conclusion_date=datetime.utcnow())
            form = self.form_cls(flask.request.form)

        elif conclusion_id:
            new_conclusion = False
            self.conclusion = (self.comment_cls
                                    .query.get_or_404(conclusion_id))
            perm_edit_comment(self.conclusion).test()
            self.record = self.record_for_comment(self.conclusion)
            old_data = self.parse_commentform(self.conclusion)
            if flask.request.method == 'POST':
                form_data = flask.request.form
            else:
                form_data = MultiDict(flatten_dict(old_data))
            form = self.form_cls(form_data)

        else:
            raise RuntimeError("Need at least one of "
                               "record_id and conclusion_id")

        self.setup_template_context()
        self.template_ctx['next_url'] = flask.request.args.get('next')

        if flask.request.method == 'POST' and form.validate():
            self.link_conclusion_to_record()

            self.flatten_commentform(form.data, self.conclusion)
            models.db.session.add(self.conclusion)

            app = flask.current_app._get_current_object()
            if new_conclusion:
                self.add_signal.send(app, ob=self.conclusion,
                                          new_data=form.data)
            else:
                self.edit_signal.send(app, ob=self.conclusion,
                                      old_data=old_data, new_data=form.data)

            models.db.session.commit()

            return flask.render_template(self.template_saved,
                                         **self.template_ctx)

        self.template_ctx['form'] = form
        return flask.render_template(self.template, **self.template_ctx)


class CommentStateView(flask.views.View):

    methods = ['POST']

    def dispatch_request(self, conclusion_id):
        conclusion = self.comment_cls.query.get_or_404(conclusion_id)
        next_url = flask.request.form['next']
        new_status = flask.request.form['status']
        if new_status not in STATUS_VALUES:
            flask.abort(403)
        old_status = conclusion.status
        conclusion.status = new_status
        app = flask.current_app._get_current_object()
        self.signal.send(app, ob=conclusion,
                         old_data=old_status, new_data=new_status)
        models.db.session.commit()
        return flask.redirect(next_url)


class CommentDeleteView(flask.views.View):

    methods = ['POST']

    def dispatch_request(self, conclusion_id):
        conclusion = self.comment_cls.query.get_or_404(conclusion_id)
        perm_delete_comment(conclusion).test()
        next_url = flask.request.form['next']
        conclusion.deleted = True
        app = flask.current_app._get_current_object()
        old_data = self.parse_commentform(conclusion)
        old_data['_status'] = conclusion.status
        self.signal.send(app, ob=conclusion, old_data=old_data)
        models.db.session.commit()
        return flask.redirect(next_url)
