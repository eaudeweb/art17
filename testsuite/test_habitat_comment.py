# encoding: utf-8

import pytest

COMMENT_SAVED_TXT = "Comentariul a fost înregistrat"
MISSING_FIELD_TXT = "Suprafața este obligatorie"

HABITAT_STRUCT_DATA = {
    'range': {
        'surface_area': 123,
        'method': '1',
        'trend_short': {
            'trend': '+',
            'period': {
                'start': 'amin',
                'end': 'amax',
            },
        },
        'trend_long': {
            'trend': '-',
            'period': {
                'start': 'bmin',
                'end': 'bmax',
            },
        },
        'reference_value': {
            'method': 'foo method',
            'number': 456,
            'op': '>',
            'x': None,
        },
        'conclusion': {
            'value': 'U1',
            'trend': 'foo conclusion trend',
        },
    },
}


HABITAT_MODEL_DATA = {
    'range_surface_area': 123,
    'range_method': '1',
    'range_trend': '+',
    'range_trend_period': 'aminamax',
    'range_trend_long': '-',
    'range_trend_long_period': 'bminbmax',
    'complementary_favourable_range_op': '>',
    'complementary_favourable_range': 456,
    'complementary_favourable_range_method': 'foo method',
    'conclusion_range': 'U1',
    'conclusion_range_trend': 'foo conclusion trend',
}


def _create_habitat_record(habitat_app, comment=False):
    from art17 import models
    with habitat_app.app_context():
        habitat = models.DataHabitat(id=1, habitatcode='1234')
        habitat.lu = models.LuHabitattypeCodes(objectid=1, code=1234)
        record = models.DataHabitattypeRegion(id=1, hr_habitat=habitat,
                                              region='ALP')
        record.lu = models.LuBiogeoreg(objectid=1)
        models.db.session.add(record)

        if comment:
            comment = models.DataHabitattypeComment(id='4f799fdd6f5a',
                                                    habitat_id=1,
                                                    region='ALP',
                                                    range_surface_area=1337)
            models.db.session.add(comment)

        models.db.session.commit()


def test_load_comments_view(habitat_app):
    _create_habitat_record(habitat_app)
    client = habitat_app.test_client()
    resp = client.get('/habitate/detalii/1/comentariu')
    assert resp.status_code == 200


def test_save_comment_record(habitat_app):
    from art17.models import DataHabitattypeComment
    _create_habitat_record(habitat_app)
    client = habitat_app.test_client()
    resp = client.post('/habitate/detalii/1/comentariu',
                       data={'range.surface_area': '50',
                             'range.method': '1'})
    assert resp.status_code == 200
    assert COMMENT_SAVED_TXT in resp.data
    with habitat_app.app_context():
        assert DataHabitattypeComment.query.count() == 1
        comment = DataHabitattypeComment.query.first()
        assert comment.hr_habitat.habitatcode == '1234'
        assert comment.region == 'ALP'
        assert comment.range_surface_area == 50


def test_error_on_required_record(habitat_app):
    from art17.models import DataHabitattypeComment
    _create_habitat_record(habitat_app)
    client = habitat_app.test_client()
    resp = client.post('/habitate/detalii/1/comentariu',
                       data={'range.surface_area': ''})
    assert resp.status_code == 200
    assert COMMENT_SAVED_TXT not in resp.data
    assert MISSING_FIELD_TXT in resp.data
    with habitat_app.app_context():
        assert DataHabitattypeComment.query.count() == 0


def test_edit_comment_form(habitat_app):
    from art17.models import DataHabitattypeComment, db
    _create_habitat_record(habitat_app, comment=True)
    client = habitat_app.test_client()
    resp1 = client.get('/habitate/comentariu/f3b4c23bcb88')
    assert resp1.status_code == 404
    resp2 = client.get('/habitate/comentariu/4f799fdd6f5a')
    assert resp2.status_code == 200
    assert '1337' in resp2.data


def test_edit_comment_submit(habitat_app):
    from art17.models import DataHabitattypeComment, db
    _create_habitat_record(habitat_app, comment=True)
    client = habitat_app.test_client()
    resp = client.post('/habitate/comentariu/4f799fdd6f5a',
                       data={'range.surface_area': '50',
                             'range.method': '1'})
    assert resp.status_code == 200
    assert COMMENT_SAVED_TXT in resp.data
    with habitat_app.app_context():
        comment = DataHabitattypeComment.query.get('4f799fdd6f5a')
        assert comment.range_surface_area == 50


def test_save_all_form_fields():
    from art17 import forms
    from art17 import models
    from art17.common import flatten_dict
    from art17.schemas import flatten_habitat_commentform
    from werkzeug.datastructures import MultiDict

    form_data = MultiDict(flatten_dict(HABITAT_STRUCT_DATA))

    form = forms.HabitatComment(form_data)
    assert form.validate()

    comment = models.DataHabitattypeComment()
    flatten_habitat_commentform(form.data, comment)

    for k, v in HABITAT_MODEL_DATA.items():
        assert getattr(comment, k) == v


def test_flatten():
    from art17.schemas import flatten_habitat_commentform
    from art17 import models
    obj = models.DataHabitattypeComment()
    flatten_habitat_commentform(HABITAT_STRUCT_DATA, obj)
    for k, v in HABITAT_MODEL_DATA.items():
        assert getattr(obj, k) == v


def test_parse():
    from art17.schemas import parse_habitat_commentform
    from art17 import models
    obj = models.DataHabitattypeComment(**HABITAT_MODEL_DATA)
    data = parse_habitat_commentform(obj)
    assert data == HABITAT_STRUCT_DATA


def test_add_comment_message(habitat_app):
    import flask
    from webtest import TestApp
    from art17.messages import messages
    from art17 import models

    _create_habitat_record(habitat_app, comment=True)
    habitat_app.register_blueprint(messages)
    client = TestApp(habitat_app)
    page = client.get('/mesaje/4f799fdd6f5a/nou')
    form = page.forms['message-form']
    form['text'] = "hello world!"
    form.submit()

    with habitat_app.app_context():
        messages = models.CommentMessage.query.all()
        assert len(messages) == 1
        msg = messages[0]
        assert msg.text == "hello world!"
        assert msg.user_id == 'somewho'
        assert msg.parent == '4f799fdd6f5a'
