from werkzeug.datastructures import MultiDict
import pytest


NOT_VALID = object()


@pytest.mark.parametrize(['formdata', 'valid_data'], [
    # all values are blank
    [{'trend': '', 'period.start': '', 'period.end': ''},
     {'trend': '', 'period': {'start': None, 'end': None}}],

    # trend and both years filled in
    [{'trend': '+', 'period.start': '2010', 'period.end': '2013'},
     {'trend': '+', 'period': {'start': 2010, 'end': 2013}}],

    # years filled in with bogus data
    [{'trend': '+', 'period.start': 'asdf', 'period.end': 'qwer'},
     NOT_VALID],

    # only first year filled in
    [{'trend': '+', 'period.start': '2010', 'period.end': ''},
     NOT_VALID],

    # only second year filled in
    [{'trend': '+', 'period.start': '', 'period.end': '2013'},
     NOT_VALID],

    # years filled in but no trend
    [{'trend': '', 'period.start': '2010', 'period.end': '2013'},
     NOT_VALID],

    # trend filled in but no years
    [{'trend': '+', 'period.start': '', 'period.end': ''},
     NOT_VALID],
])
def test_period_validation(formdata, valid_data):
    from art17 import forms
    form = forms.Trend(MultiDict(formdata))

    if valid_data is NOT_VALID:
        assert not form.validate()

    else:
        assert form.validate()
        assert form.data == valid_data
