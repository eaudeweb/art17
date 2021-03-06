# encoding: utf-8

from datetime import datetime
import urllib
import flask
from art17 import models, config
from art17 import species
from art17 import habitat
from art17 import replies
from art17.aggregation import (
    species_record_finalize, species_record_definalize,
    habitat_record_definalize, habitat_record_finalize,
)
from art17.aggregation.utils import get_history_aggregation_record_url
from art17.common import (
    json_encode_more,
    perm_view_history,
    get_history_object_url,
)
from art17.auth import admin_permission
from art17.dal import get_biogeo_region
from art17.pagination import Paginator
from art17.forms import ActivityFilterForm
from art17 import DATE_FORMAT_HISTORY

history = flask.Blueprint('history', __name__)
history_consultation = flask.Blueprint('history_consultation', __name__)
history_aggregation = flask.Blueprint('history_aggregation', __name__)

TABLE_LABEL = {
    'data_species_regions': u"evaluare specie",
    'data_habitattype_regions': u"evaluare habitat",
    'comment_replies': u"replică",
}

ACTIONS_TRANSLATION = {
    ('data_species_regions', 'add'): u'adăugare comentariu',
    ('data_species_regions', 'edit'): u'modificare comentariu',
    ('data_species_regions', 'status'): u'evaluare comentariu',
    ('data_species_regions', 'delete'): u'ștergere comentariu',
    ('data_habitattype_regions', 'add'): u'adăugare comentariu',
    ('data_habitattype_regions', 'edit'): u'modificare comentariu',
    ('data_habitattype_regions', 'status'): u'evaluare comentariu',
    ('data_habitattype_regions', 'delete'): u'ștergere comentariu',
    ('comment_replies', 'add'): u'adăugare replică',
    ('comment_replies', 'delete'): u'ștergere replică',
}

ACTIONS_TRANSLATION_AGG = {
    ('data_species_regions', 'edit'): u'modificare înregistrare',
    ('data_species_regions', 'finalize'): u'finalizare',
    ('data_species_regions', 'definalize'): u'definalizare',
    ('data_habitattype_regions', 'edit'): u'modificare înregistrare',
    ('data_habitattype_regions', 'finalize'): u'finalizare',
    ('data_habitattype_regions', 'definalize'): u'definalizare',
}

PER_PAGE = 25


@history.record
def register_handlers(state):
    app = state.app

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
    connect(replies.reply_removed, app,
            table='comment_replies', action='remove')


@history_aggregation.record
def register_aggregation_handlers(state):
    app = state.app

    connect(species_record_finalize, app,
            table='data_species_regions', action='finalize')
    connect(species_record_definalize, app,
            table='data_species_regions', action='definalize')
    connect(habitat_record_finalize, app,
            table='data_habitattype_regions', action='finalize')
    connect(habitat_record_definalize, app,
            table='data_habitattype_regions', action='definalize')


def connect(signal, sender, **more_kwargs):
    @signal.connect_via(sender)
    def wrapper(sender, **kwargs):
        kwargs.update(more_kwargs)
        handle_signal(**kwargs)


def handle_signal(table, action, ob, old_data=None, new_data=None, **extra):
    if not ob.id:
        models.db.session.flush()
        assert ob.id
    if table == 'comment_replies':
        record = replies.get_comment_from_reply(ob.parent_table,
                                                ob.parent_id)
        dataset_id = record.cons_dataset_id if record else None
    else:
        dataset_id = ob.cons_dataset_id
    item = models.History(table=table,
                          action=action,
                          object_id=ob.id,
                          dataset_id=dataset_id,
                          date=datetime.now(),
                          user_id=flask.g.identity.id)
    if old_data:
        item.old_data = flask.json.dumps(old_data, default=json_encode_more)
    if new_data:
        item.new_data = flask.json.dumps(new_data, default=json_encode_more)
    models.db.session.add(item)


@history_consultation.context_processor
@history_aggregation.context_processor
def inject_lookup_tables():
    return {
        'TABLE_LABEL': TABLE_LABEL,
    }


@history_consultation.route('/activitate')
@history_aggregation.route('/dataset/<int:dataset_id>/activitate')
@admin_permission.require()
def index(dataset_id=None):
    if dataset_id:
        # Aggregation
        base_url = flask.url_for('.index', dataset_id=dataset_id)
        item_url = get_history_aggregation_record_url
        history_items = (
            models.History.query
            .filter_by(dataset_id=dataset_id)
            .filter(
                models.History.table.startswith('data_habitattype_regions') |
                models.History.table.startswith('data_species_regions')
            )
            .order_by(models.History.date.desc())
        )
        TRANS = ACTIONS_TRANSLATION_AGG
    else:
        # Consultation
        base_url = flask.url_for('.index')
        item_url = get_history_object_url
        dataset_id = config.get_config_value('CONSULTATION_DATASET', '1')
        history_items = (
            models.History.query
            .filter_by(dataset_id=dataset_id)
            .order_by(models.History.date.desc())
        )
        TRANS = ACTIONS_TRANSLATION
    page = int(flask.request.args.get('page', 1))
    start_date = flask.request.args.get('start_date', '')
    end_date = flask.request.args.get('end_date', '')
    user_id = flask.request.args.get('user_id', '')

    form = ActivityFilterForm(start_date=start_date, end_date=end_date,
                              user_id=user_id)
    form.set_user_choices(dataset_id)

    if start_date:
        start_date = datetime.strptime(start_date, DATE_FORMAT_HISTORY)
        history_items = history_items.filter(models.History.date >= start_date)
    if end_date:
        end_date = datetime.strptime(end_date, DATE_FORMAT_HISTORY)
        history_items = history_items.filter(models.History.date <= end_date)
    if user_id:
        history_items = history_items.filter_by(user_id=user_id)

    count = history_items.count()
    history_items = history_items.paginate(page, PER_PAGE, False).items
    paginator = Paginator(per_page=PER_PAGE, page=page, count=count)

    for item in history_items:
        result = item_url(item)
        if result:
            item.url, title, region = result
            item.title = u'{0} - {1}'.format(title, region)
        else:
            item.url = result
        item.action = TRANS.get(
            (item.table.strip(), item.action), item.action)


    get_params = flask.request.args.to_dict()
    get_params.pop('page', None)
    query_string = urllib.urlencode(get_params)

    return flask.render_template('history/index.html', **{
        'history_items': history_items,
        'dataset_id': dataset_id,
        'paginator': paginator,
        'base_url': base_url,
        'query_string': query_string,
        'form': form,
    })


@history_consultation.route('/activitate/<item_id>')
@history_aggregation.route('/activitate/<item_id>')
@admin_permission.require()
def delta(item_id):
    return flask.render_template('history/delta.html', **{
        'item': models.History.query.get_or_404(item_id),
    })


@history.app_template_filter('pretty_json_data')
def pretty_json_data(json_data):
    data = flask.json.loads(json_data)
    return flask.json.dumps(data, indent=2, sort_keys=True)


@history_consultation.route('/activitate/specii/<subject_code>/<region_code>')
@history_aggregation.route('/dataset/<int:dataset_id>/activitate'
                           '/specii/<subject_code>/<region_code>')
def species_comments(subject_code, region_code, dataset_id=None):
    from art17.species import get_dal

    dataset = get_dal(dataset_id)
    items = dataset.get_history(subject_code, region_code)
    subject = dataset.get_subject(subject_code)
    perm_view_history(subject).test()
    return flask.render_template('history/comments.html', **{
        'history_items': items,
        'subject_category': 'specii',
        'subject_code': subject_code,
        'subject': subject,
        'region': get_biogeo_region(region_code),
        'dashboard_url':
            flask.url_for('dashboard.species',
                          group_code=subject.lu.group_code)
            if dataset_id is None else '',
        'record_index_url':
            flask.url_for('species.index', region=region_code,
                          species=subject_code)
            if dataset_id is None else '',
        'region_code': region_code,
    })


@history_consultation.route(
    '/activitate/habitate/<subject_code>/<region_code>')
@history_aggregation.route('/dataset/<int:dataset_id>/activitate'
                           '/habitate/<subject_code>/<region_code>')
def habitat_comments(subject_code, region_code, dataset_id=None):
    from art17.habitat import get_dal

    dataset = get_dal(dataset_id)
    items = dataset.get_history(subject_code, region_code)
    subject = dataset.get_subject(subject_code)
    perm_view_history(subject).test()

    return flask.render_template('history/comments.html', **{
        'history_items': items,
        'subject_category': 'habitate',
        'subject_code': subject_code,
        'subject': subject,
        'region': get_biogeo_region(region_code),
        'dashboard_url':
            flask.url_for('dashboard.habitats') if dataset_id is None else '',
        'record_index_url':
            flask.url_for('habitat.index', region=region_code,
                          habitat=subject_code) if dataset_id is None else '',
        'region_code': region_code,
    })
