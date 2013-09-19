import flask
from blinker import Signal
from art17 import models
from art17.common import IndexView, CommentView, CommentStateView
from art17 import forms
from art17 import schemas

habitat = flask.Blueprint('habitat', __name__)

comment_added = Signal()
comment_edited = Signal()
comment_status_changed = Signal()


@habitat.route('/habitate/regiuni/<int:habitat_code>')
def lookup_regions(habitat_code):
    habitat = (models.DataHabitat.query
                .filter_by(code=habitat_code)
                .first_or_404())
    regions = [{'id': r.lu.code, 'text': r.lu.name_ro}
               for r in habitat.regions.join(models.DataHabitattypeRegion.lu)]
    return flask.jsonify(options=regions)


class HabitatIndexView(IndexView):

    template = 'habitat/index.html'
    subject_name = 'habitat'
    subject_cls = models.DataHabitat
    record_cls = models.DataHabitattypeRegion
    parse_record = staticmethod(schemas.parse_habitat)
    records_template = 'habitat/records.html'

    @property
    def map_url_template(self):
        return flask.current_app.config['HABITAT_MAP_URL']

    def get_subject_list(self):
        return [{'id': h.code, 'text': h.lu.display_name}
                for h in self.subject_list]


habitat.add_url_rule('/habitate/', view_func=HabitatIndexView.as_view('index'))


@habitat.route('/habitate/detalii/<int:record_id>')
def detail(record_id):
    record = models.DataHabitattypeRegion.query.get_or_404(record_id)
    return flask.render_template('habitat/detail.html', **{
        'habitat': record.hr_habitat,
        'record': schemas.parse_habitat(record),
    })


class HabitatCommentView(CommentView):

    form_cls = forms.HabitatComment
    record_cls = models.DataHabitattypeRegion
    comment_cls = models.DataHabitattypeComment
    parse_commentform = staticmethod(schemas.parse_habitat_commentform)
    flatten_commentform = staticmethod(schemas.flatten_habitat_commentform)
    template = 'habitat/comment.html'
    template_saved = 'habitat/comment-saved.html'
    add_signal = comment_added
    edit_signal = comment_edited

    def link_comment_to_record(self):
        self.comment.habitat_id = self.record.habitat_id
        self.comment.region = self.record.region

    def setup_template_context(self):
        self.template_ctx = {
            'habitat': self.record.hr_habitat,
            'record': schemas.parse_habitat(self.record),
        }

    def record_for_comment(self, comment):
        records = (models.DataHabitattypeRegion.query
                            .filter_by(habitat_id=comment.habitat_id)
                            .filter_by(region=comment.region)
                            .all())
        assert len(records) == 1, "Expected exactly one record for the comment"
        return records[0]


habitat.add_url_rule('/habitate/detalii/<int:record_id>/comentariu',
                     view_func=HabitatCommentView.as_view('comment'))


habitat.add_url_rule('/habitate/comentariu/<comment_id>',
                     view_func=HabitatCommentView.as_view('comment_edit'))


class HabitatCommentStateView(CommentStateView):

    comment_cls = models.DataHabitattypeComment
    signal = comment_status_changed


habitat.add_url_rule('/habitate/comentariu/<comment_id>/stare',
                view_func=HabitatCommentStateView.as_view('comment_status'))
