# encoding: utf-8

import json
from wtforms import (Form as Form_base, FormField as FormField_base,
                     TextField, TextAreaField, DecimalField, SelectField,
                     IntegerField, SelectMultipleField, BooleanField)
from wtforms.validators import Required, Optional, NumberRange
from wtforms.widgets import HTMLString, html_params
from werkzeug.datastructures import MultiDict
from wtforms.compat import text_type

from art17 import models
from art17.lookup import (
    TREND_OPTIONS,
    CONCLUSION_OPTIONS,
    METHODS_USED_OPTIONS,
    LU_FV_RANGE_OP_OPTIONS,
    LU_FV_RANGE_OP_FUNCT_OPTIONS,
    LU_REASONS_FOR_CHANGE,
    QUALITY_OPTIONS,
    METHODS_PRESSURES_OPTIONS,
    METHODS_THREATS_OPTIONS
    )
from art17 import schemas

EMPTY_CHOICE = [('', "")]


def all_fields(form):
    for field in form:
        if hasattr(field, 'form'):
            for subfield in all_fields(field.form):
                yield subfield
        else:
            yield field


class MultipleHiddenWidget(object):
    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        html = []
        for val in field.data:
            html.append(self.render_input(field, val))
        return HTMLString(''.join(html))

    @classmethod
    def render_input(cls, field, val):
        val = json.dumps(val)
        return HTMLString('<input type="hidden" %s %s />' % (
            html_params(name=field.name),
            html_params(value=val)))


class MultipleJSONField(SelectMultipleField):
    widget = MultipleHiddenWidget()

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('coerce', json.loads)
        super(MultipleJSONField, self).__init__(*args, **kwargs)

    def iter_choices(self):
        return []

    def pre_validate(self, form):
        if self.data:
            check_list = []
            for obj in self.data:
                if obj in check_list:
                    raise ValueError('Duplicate values')
                check_list.append(obj)

    def render_input(self, val):
        return self.widget.render_input(self, val)


class SpeciesField(TextAreaField):

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = [l.strip() for l in valuelist[0].split('\n')]
        else:
            self.data = []

    def _value(self):
        data = '\n'.join(self.data) if self.data is not None else ''
        return text_type(data)


class MeasureField(BooleanField):
    def _value(self):
        return '1'


class FormValidator(object):
    def __init__(self, form):
        self.validation_form = form

    def __call__(self, form, field):
        data = field.data

        form = self.validation_form()
        for i, d in enumerate(data):
            form.process(MultiDict(d))
            if not form.validate():
                raise ValueError('Invalid values on line ' + str(i + 1))


class FormField(FormField_base):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('separator', '.')
        super(FormField, self).__init__(*args, **kwargs)


class Form(Form_base):
    def validate(self):
        if not super(Form, self).validate():
            return False

        return self.custom_validate()

    def custom_validate(self):
        return True


class PopulationValue(Form):
    unit = SelectField(default='', validators=[Optional()])
    min = DecimalField(
        validators=[Optional(u"Mǎrimea trebuie sǎ fie de tip numeric")])
    max = DecimalField(
        validators=[Optional(u"Mǎrimea trebuie sǎ fie de tip numeric")])


class AreaValue(Form):
    min = DecimalField(
        validators=[Optional(u"Mǎrimea trebuie sǎ fie de tip numeric")])
    max = DecimalField(
        validators=[Optional(u"Mǎrimea trebuie sǎ fie de tip numeric")])


class MagnitudeValue(AreaValue):
    pass


class MagnitudeCIValue(MagnitudeValue):
    ci = DecimalField(label=u"interval de încredere", validators=[Optional()])


class Period(Form):
    start = IntegerField(label=u"an de început",
                         validators=[Optional(), NumberRange(1900, 2100)])
    end = IntegerField(label=u"an de sfârșit",
                       validators=[Optional(), NumberRange(1900, 2100)])


def set_required_error_message(field):
    message = u'Completați câmpul "%s"' % field.label.text
    field.errors.append(message)


def set_only_one_error_message(fields):
    message = u"Doar unul dintre: %s poate fi completat" % \
              (', '.join([f.label.text for f in fields])
    )
    fields[0].errors.append(message)


class Trend(Form):
    trend = SelectField(choices=EMPTY_CHOICE + TREND_OPTIONS,
                        default='',
                        label=u"tendință",
                        validators=[Optional()])
    period = FormField(Period)
    magnitude = FormField(MagnitudeValue)

    def custom_validate(self):
        fields = [self.period.start, self.period.end, self.trend]
        empty = [f for f in fields if not f.data]

        if empty and len(empty) < len(fields):
            for field in empty:
                set_required_error_message(field)
            return False

        return True


class TrendCI(Trend):
    magnitude = FormField(MagnitudeCIValue)
    method = SelectField(default='',
                         choices=EMPTY_CHOICE + METHODS_USED_OPTIONS,
                         validators=[Optional()],
    )


class ReferenceValue(Form):
    op = SelectField(default='', label=u"operator", validators=[Optional()])
    number = DecimalField(label=u"suprafață", validators=[Optional()])
    x = BooleanField(label=u"necunoscut", validators=[Optional()])
    method = TextAreaField(validators=[Optional()])

    def custom_validate(self):
        fields = [self.number, self.op, self.x]
        filled = [f for f in fields if f.data]

        if len(filled) > 1:
            set_only_one_error_message(filled)
            return False

        return True


class ReasonValue(Form):
    a = MeasureField(default=False, label=LU_REASONS_FOR_CHANGE['a'],
                     validators=[Optional()])
    b = MeasureField(default=False, label=LU_REASONS_FOR_CHANGE['b'],
                     validators=[Optional()])
    c = MeasureField(default=False, label=LU_REASONS_FOR_CHANGE['c'],
                     validators=[Optional()])


class Conclusion(Form):
    value = SelectField(choices=EMPTY_CHOICE + CONCLUSION_OPTIONS,
                        default='',
                        validators=[Optional()])
    trend = SelectField(choices=EMPTY_CHOICE + TREND_OPTIONS,
                        default='',
                        validators=[Optional()])


class PopulationSize(Form):
    population = FormField(PopulationValue)
    population_alt = FormField(PopulationValue)

    def __init__(self, *args, **kwargs):
        super(PopulationSize, self).__init__(*args, **kwargs)
        self.population.unit.choices = EMPTY_CHOICE + list(
                        models.db.session.query(
                            models.LuPopulationRestricted.code,
                            models.LuPopulationRestricted.name_ro))

        self.population_alt.unit.choices = EMPTY_CHOICE + list(
                        models.db.session.query(
                            models.LuPopulation.code,
                            models.LuPopulation.name_ro))


class Range(Form):
    surface_area = DecimalField(label=u"Suprafață",
        validators=[Optional(u"Mǎrimea trebuie sǎ fie de tip numeric")])
    method = SelectField(default='',
                         choices=EMPTY_CHOICE + METHODS_USED_OPTIONS)
    trend_short = FormField(Trend)
    trend_long = FormField(Trend)
    reference_value = FormField(ReferenceValue)
    reason = FormField(ReasonValue)
    conclusion = FormField(Conclusion)

    def __init__(self, *args, **kwargs):
        super(Range, self).__init__(*args, **kwargs)
        self.reference_value.op.choices = EMPTY_CHOICE + LU_FV_RANGE_OP_OPTIONS


class Population(Form):
    size = FormField(PopulationSize)
    additional_locality = TextAreaField(validators=[Optional()])
    additional_method = TextAreaField(validators=[Optional()])
    additional_problems = TextAreaField(validators=[Optional()])
    date = TextField(validators=[Optional()])
    method = SelectField(default='',
                         choices=EMPTY_CHOICE + METHODS_USED_OPTIONS)
    trend_short = FormField(TrendCI)
    trend_long = FormField(TrendCI)
    reference_value = FormField(ReferenceValue)
    reason = FormField(ReasonValue)
    conclusion = FormField(Conclusion)

    def __init__(self, *args, **kwargs):
        super(Population, self).__init__(*args, **kwargs)
        self.reference_value.op.choices = EMPTY_CHOICE + LU_FV_RANGE_OP_FUNCT_OPTIONS


class Habitat(Form):
    surface_area = DecimalField(
        validators=[Optional(u"Mǎrimea trebuie sǎ fie de tip numeric")])
    date = TextField(validators=[Optional()])
    method = SelectField(default='',
                         choices=EMPTY_CHOICE + METHODS_USED_OPTIONS)
    quality = SelectField(default='',
                          choices=EMPTY_CHOICE + QUALITY_OPTIONS)
    quality_explanation = TextAreaField()
    trend_short = FormField(Trend)
    trend_long = FormField(Trend)
    area_suitable = DecimalField(
        validators=[Optional(u"Mǎrimea trebuie sǎ fie de tip numeric")])
    reason = FormField(ReasonValue)
    conclusion = FormField(Conclusion)


class Coverage(Form):
    surface_area = DecimalField(
        validators=[Optional(u"Mǎrimea trebuie sǎ fie de tip numeric")])
    date = TextField(validators=[Optional()])
    method = SelectField(default='',
                         choices=EMPTY_CHOICE + METHODS_USED_OPTIONS)
    trend_short = FormField(TrendCI)
    trend_long = FormField(TrendCI)
    reference_value = FormField(ReferenceValue)
    reason = FormField(ReasonValue)
    conclusion = FormField(Conclusion)

    def __init__(self, *args, **kwargs):
        super(Coverage, self).__init__(*args, **kwargs)
        self.reference_value.op.choices = EMPTY_CHOICE + LU_FV_RANGE_OP_FUNCT_OPTIONS


class PressureForm(Form):
    pressure = SelectField(default='')
    ranking = SelectField(default='')
    pollutions = SelectMultipleField(default='')

    def __init__(self, *args, **kwargs):
        super(PressureForm, self).__init__(*args, **kwargs)
        self.pressure.choices = EMPTY_CHOICE + [(p[0], '%s. %s' % p) for p in
                                                models.db.session.query(
                                                    models.LuThreats.code,
                                                    models.LuThreats.name)]
        self.ranking.choices = EMPTY_CHOICE + list(models.db.session.query(
            models.LuRanking.code,
            models.LuRanking.name_ro))
        self.pollutions.choices = [(p[0], '%s %s' % p) for p in
                                   models.db.session.query(
                                       models.LuPollution.code,
                                       models.LuPollution.name_ro)]


class Pressures(Form):
    pressures_method = SelectField(default='',
                                   choices=EMPTY_CHOICE +
                                           METHODS_PRESSURES_OPTIONS)
    pressures = MultipleJSONField(default='',
                                  validators=[FormValidator(PressureForm)])


class Threats(Form):
    threats_method = SelectField(default='',
                                 choices=EMPTY_CHOICE +
                                         METHODS_PRESSURES_OPTIONS)
    threats = MultipleJSONField(default='',
                                validators=[FormValidator(PressureForm)])


class MeasuresForm(Form):
    measurecode = SelectField(default='')
    type_legal = MeasureField(default=False)
    type_administrative = MeasureField(default=False)
    type_contractual = MeasureField(default=False)
    type_recurrent = MeasureField(default=False)
    type_oneoff = MeasureField(default=False)
    rankingcode = SelectField(default='')
    location_inside = MeasureField(default=False)
    location_outside = MeasureField(default=False)
    location_both = MeasureField(default=False)
    broad_evaluation_maintain = MeasureField(default=False)
    broad_evaluation_enhance = MeasureField(default=False)
    broad_evaluation_longterm = MeasureField(default=False)
    broad_evaluation_noeffect = MeasureField(default=False)
    broad_evaluation_unknown = MeasureField(default=False)
    broad_evaluation_notevaluat_18 = MeasureField(default=False)

    def __init__(self, *args, **kwargs):
        super(MeasuresForm, self).__init__(*args, **kwargs)
        self.measurecode.choices = EMPTY_CHOICE + list(models.db.session.query(
            models.LuMeasures.code,
            models.LuMeasures.name_ro))
        self.rankingcode.choices = EMPTY_CHOICE + list(models.db.session.query(
            models.LuRanking.code,
            models.LuRanking.name_ro))


class Measures(Form):
    measures = MultipleJSONField(default='')


class Infocomp(Form):

    justification = TextField(validators=[Optional()])
    other_relevant_information = TextField(validators=[Optional()])
    transboundary_assessment = TextField(validators=[Optional()])


class Natura2000Species(Form):

    population = FormField(PopulationValue)
    method = SelectField(default='',
                         choices=EMPTY_CHOICE + METHODS_USED_OPTIONS,
                         validators=[Optional()],
    )
    trend = SelectField(
        choices=EMPTY_CHOICE + TREND_OPTIONS,
        default='',
        validators=[Optional()]
    )

    def __init__(self, *args, **kwargs):
        super(Natura2000Species, self).__init__(*args, **kwargs)
        self.population.unit.choices = EMPTY_CHOICE + list(
                        models.db.session.query(
                            models.LuPopulation.code,
                            models.LuPopulation.name_ro))


class Natura2000Habitat(Form):

    area = FormField(AreaValue)
    method = SelectField(default='',
                         choices=EMPTY_CHOICE + METHODS_USED_OPTIONS,
                         validators=[Optional()],
    )
    trend = SelectField(
        choices=EMPTY_CHOICE + TREND_OPTIONS,
        default='',
        validators=[Optional()]
    )


class TypicalSpecies(Form):

    species = SpeciesField(default='', validators=[Optional()])
    method = TextField(validators=[Optional()])
    justification = TextField(validators=[Optional()])
    structure_and_functions_method = SelectField(default='',
                         choices=EMPTY_CHOICE + METHODS_USED_OPTIONS,
                         validators=[Optional()],
    )
    other_relevant_information = TextAreaField(validators=[Optional()])


class SpeciesComment(Form):
    range = FormField(Range)
    population = FormField(Population)
    habitat = FormField(Habitat)
    pressures = FormField(Pressures)
    threats = FormField(Threats)
    infocomp = FormField(Infocomp)
    natura2000 = FormField(Natura2000Species)
    measures = FormField(Measures)
    future_prospects = FormField(Conclusion)
    overall_assessment = FormField(Conclusion)
    report_observation = TextAreaField(validators=[Optional()])
    generalstatus = SelectField(default='1')
    published = TextAreaField(validators=[Optional()])

    def __init__(self, *args, **kwargs):
        super(SpeciesComment, self).__init__(*args, **kwargs)
        self.generalstatus.choices = models.db.session.query(
            models.LuPresence.code,
            models.LuPresence.name_ro)

    def custom_validate(self):
        generalstatus_field = self.generalstatus
        fields = list(f for f in all_fields(self) if f != generalstatus_field)
        empty = [f for f in fields if not f.data]

        if empty and len(empty) == len(fields):
            if generalstatus_field.data == '1':
                fields[0].errors.append(u"Completați cel puțin o valoare.")
                return False

        return True

    def final_validate(self):
        mandatory_fields = (
            self.range.surface_area,
            self.range.method,
            self.range.trend_short.trend,
            self.range.trend_short.period,
            self.range.reference_value.method,
            self.population.date,
            self.population.method,
            self.population.trend_short.trend,
            self.population.trend_short.period,
            self.population.trend_short.method,
            self.population.reference_value.method,
            self.habitat.surface_area,
            self.habitat.date,
            self.habitat.method,
            self.habitat.quality,
            self.habitat.quality_explanation,
            self.habitat.trend_short.trend,
            self.habitat.trend_short.period,
            self.habitat.area_suitable,
            self.pressures.pressures,
            self.pressures.pressures_method,
            self.threats.threats,
            self.threats.threats_method,
            self.range.conclusion.value,
            self.population.conclusion.value,
            self.habitat.conclusion.value,
            self.future_prospects.value,
            self.overall_assessment.value,
            self.overall_assessment.trend,
            self.natura2000.population.unit,
            self.natura2000.population.min,
            self.natura2000.population.max,
            self.natura2000.method,
        )

        try:
            self.validate()
        finally:
            for f in mandatory_fields:
                if not f.data:
                    f.errors.append(
                        u"Trebuie completat câmpul %s" % (f.label.text or f)
                    )
            if not (self.population.size.population.unit.data or
                        self.population.size.population_alt.unit.data):
                self.population.size.population.unit.errors.append(
                    u"Trebuie completată una dintre cele două dimensiuni"
                    u" ale populației"
                )

        return not self.errors


class HabitatComment(Form):
    range = FormField(Range)
    coverage = FormField(Coverage)
    pressures = FormField(Pressures)
    threats = FormField(Threats)
    typicalspecies = FormField(TypicalSpecies)
    natura2000 = FormField(Natura2000Habitat)
    measures = FormField(Measures)
    structure = FormField(Conclusion)
    future_prospects = FormField(Conclusion)
    overall_assessment = FormField(Conclusion)
    report_observation = TextAreaField(validators=[Optional()])
    published = TextAreaField(validators=[Optional()])

    def custom_validate(self):
        fields = list(all_fields(self))
        empty = [f for f in fields if not f.data]

        if empty and len(empty) == len(fields):
            fields[0].errors.append(u"Completați cel puțin o valoare.")
            return False

        return True

    def final_validate(self):
        mandatory_fields = (
            self.range.surface_area,
            self.range.method,
            self.range.trend_short.trend,
            self.range.trend_short.period,
            self.range.reference_value.method,
            self.coverage.surface_area,
            self.coverage.date,
            self.coverage.method,
            self.coverage.trend_short.trend,
            self.coverage.trend_short.period,
            self.coverage.trend_short.method,
            self.pressures.pressures,
            self.pressures.pressures_method,
            self.threats.threats,
            self.threats.threats_method,
            self.typicalspecies.species,
            self.typicalspecies.method,
            self.typicalspecies.structure_and_functions_method,
            self.range.conclusion.value,
            self.coverage.conclusion.value,
            self.structure.value,
            self.future_prospects.value,
            self.overall_assessment.value,
            self.overall_assessment.trend,
        )

        try:
            self.validate()
        finally:
            for f in mandatory_fields:
                if not f.data:
                    f.errors.append(
                        u"Trebuie completat câmpul %s" % (f.label.text or f)
                    )

        return not self.errors
