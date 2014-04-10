# encoding: utf-8
import flask
from flask import current_app
from art17 import models
from art17 import auth

CONFIGURATION = {
    'CONSULTATION': {
        'SPECIES_MAP_URL': u"URL serviciu de hărți pentru specii",
        'HABITAT_MAP_URL': u"URL serviciu de hărți pentru habitate",
        'CONSULTATION_DATASET': u"Setul de date în consultare",
        'SPECIES_PRIMARY_DATA_URL': u"URL serviciu de date primare pentru specii",
        'HABITAT_PRIMARY_DATA_URL': u"URL serviciu de date primare pentru habitate",
    },
    'AGGREGATION': {
        'REPORTING_BEGIN': u"An de început pentru perioada de raportare",
        'REPORTING_END': u"An de final pentru perioada de raportare",
    },
}

config = flask.Blueprint('config', __name__)


@config.route('/config', methods=['GET', 'POST'])
def form():
    auth.admin_permission.test()
    config_key = current_app.config.get('CONFIG_SET', 'CONSULTATION')
    if config_key not in CONFIGURATION:
        raise ValueError('Invalid config key')

    config_set = CONFIGURATION[config_key]
    config_rows = models.Config.query.filter(
        models.Config.id.in_(config_set.keys())
    )
    if flask.request.method == 'POST':
        for row in config_rows:
            row.value = flask.request.form[row.id]
        models.db.session.commit()
        flask.flash(u"Configurația a fost salvată.", 'success')
        return flask.redirect(flask.url_for('.form'))

    return flask.render_template('config.html', **{
        'CONFIG_LABEL': config_set,
        'config_rows': config_rows,
    })


def get_config_value(name, default=''):
    row = models.Config.query.filter_by(id=name).first()
    if row and row.value:
        return row.value
    else:
        return default
