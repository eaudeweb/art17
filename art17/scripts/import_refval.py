# coding=utf-8
import os
from csv import DictReader
from art17.aggregation.refvalues import load_refval, save_refval, \
    load_species_refval, save_species_refval, load_habitat_refval, \
    save_habitat_refval
from art17.scripts import importer
from art17.models import RefValue, db


def UnicodeDictReader(utf8_data, **kwargs):
    csv_reader = DictReader(utf8_data, **kwargs)
    for row in csv_reader:
        yield {unicode(key, 'utf-8'): unicode(value, 'utf-8')
               for key, value in row.iteritems()}


SPECIES_MAP = {
    'species_magnitude.csv': 'magnitude',
    'species_range.csv': 'range',
    'species_population_range.csv': 'population_range',
    'species_population_magnitude.csv': 'population_magnitude',
    'species_population_units.csv': 'population_units',
    'species_habitat.csv': 'habitat',
}

HABITAT_MAP = {
    'habitat_magnitude.csv': 'magnitude',
    'habitat_range.csv': 'range',
    'habitat_coverage_range.csv': 'coverage_range',
    'habitat_coverage_magnitude.csv': 'coverage_magnitude',
}

METHODS = {
    'species': {
        'population_range': 'Metoda populatie',
        'range': 'Metoda areal',
        'habitat': 'Metoda suprafata habitat',
        'threats': 'Metoda amenintari',
        'pressures': 'Metoda presiuni',
    },
    'habitat': {
        'range': 'Metoda areal',
        'coverage_range': 'Metoda suprafata',
        'typical_species': 'Metoda specii tipice',
    }
}

FIELDS = {
    "range": ['Necunoscut', 'Operator - areal'],
    "coverage_range": ['Necunoscut', 'Operator'],
    "population_range": ['Necunoscut', 'Operator'],
}

DEFAULT_METHOD = '2'
REGIONS = [u'STE', u'CON', u'BLS', u'PAN', u'MBLS', u'ALP']


@importer.command
def species_refval(csv_dir='.', map=None, json_filename=None):
    json_filename = json_filename or 'species.json'
    data = load_refval(json_filename)
    map = map or SPECIES_MAP
    for filename, refval_key in map.iteritems():
        path = os.path.join(csv_dir, filename)
        if not os.path.exists(path):
            print "Missing: ", path
            continue

        with open(path, 'r') as fin:
            reader = DictReader(fin)

            for row in reader:
                if not row['Nume']:
                    # ignore groups
                    continue
                data_key = (
                    row.pop('Cod specie') + "-" + row.pop('Bioregiune')
                )
                row.pop('Nume')
                data[data_key] = data.get(data_key, {})
                data[data_key][refval_key] = row

    return save_refval(json_filename, data)


@importer.command
def habitat_refval(csv_dir='.'):
    return species_refval(csv_dir=csv_dir, map=HABITAT_MAP,
                          json_filename='habitats.json')


def set_null(d, keys):
    for k in d:
        if k in keys:
            d[k] = None


def not_null(d):
    for k, v in d.iteritems():
        if v is None:
            return False
    return True


def smart_update(data, newdata):
    for key, value in data.items():
        if key not in newdata:
            print "Ignoring: ", key, "not found in new data."
            continue
        else:
            print "Updating:", key
        for group, values in value.items():
            if group in newdata[key]:
                if not_null(newdata[key][group]):
                    vals = [data[key][group][field] for field in
                            FIELDS.get(group, [])]
                    if any(vals):
                        print 'Set Operator and Unknown to null:', key
                        set_null(data[key][group], FIELDS[group])
                data[key][group].update(newdata[key][group])
            else:
                print "Missing group:", group
    return data


@importer.command
def species_from_dataset(dataset_id=1):
    """
        Import the reference values from a previous dataset - not reference,
        but actual values.

        range:
            'Areal favorabil referinta' - r.range_surface_area
        habitat:
            u'Suprafața adecvata' - r.habitat_surface_area
        population_range:
            'Populatia favorabila de referinta' - population_alt_minimum_size
    """
    from art17.scripts.export_refval import generic_species_exporter

    def format_row(sp, sr):
        key = '{}-{}'.format(sp.code, sr.region)
        population_size = (sr.population_minimum_size or
                           sr.population_alt_minimum_size or
                           sr.population_alt_maximum_size)
        data = {
            'range': {
                'Areal favorabil referinta': unicode(
                    sr.range_surface_area) if sr.range_surface_area else None,
            },
            'habitat': {
                u'Suprafața adecvata': unicode(sr.habitat_surface_area)
                if sr.habitat_surface_area else None,
            },
            'population_range': {
                'Populatia favorabila de referinta': unicode(population_size)
                if population_size else None
            }
        }
        print key, data
        return (key, data)

    newdata = dict(generic_species_exporter(format_row, dataset_id=dataset_id))
    curdata = load_species_refval()
    data = smart_update(curdata, newdata)
    save_species_refval(data)
    print "Done."


@importer.command
def habitat_from_dataset(dataset_id=1):
    """
        Import the reference values from a previous dataset - not reference,
        but actual values.

        range:
            'Areal favorabil referinta' - r.range_surface_area
        coverage_range:
             "Suprafata favorabila referinta" - r.coverage_surface_area
    """
    from art17.scripts.export_refval import generic_habitat_exporter

    def format_row(sp, sr):
        key = '{}-{}'.format(sp.code, sr.region)
        data = {
            'range': {
                'Areal favorabil referinta': unicode(sr.range_surface_area)
                if sr.range_surface_area else None,
            },
            'coverage_range': {
                "Suprafata favorabila referinta": unicode(
                    sr.coverage_surface_area)
                if sr.coverage_surface_area else None,
            }
        }
        print key, data
        return (key, data)

    newdata = dict(generic_habitat_exporter(format_row, dataset_id=dataset_id))
    curdata = load_habitat_refval()
    data = smart_update(curdata, newdata)
    save_habitat_refval(data)
    print "Done."


def refactor_refval(json_filename, method_type):
    data = load_refval(json_filename)
    for subject, refvals in data.iteritems():
        for k, v in refvals.iteritems():
            v.pop('U1', None)
            v.pop('U2', None)
            for field, val in v.iteritems():
                if val == 'None':
                    refvals[k][field] = None
        for group, field in METHODS[method_type].iteritems():
            refvals.setdefault(group, {}).update({field: DEFAULT_METHOD})
    return data


@importer.command
def refactor_species_refval():
    data = refactor_refval('species.json', 'species')
    save_species_refval(data)


@importer.command
def refactor_habitat_refval():
    data = refactor_refval('habitats.json', 'habitat')
    save_habitat_refval(data)


@importer.command
def species_from_csv(filename, section):
    curdata = load_species_refval()
    with open(filename, 'rb') as f:
        reader = UnicodeDictReader(f)
        for row in reader:
            key = row['code'] + '-' + row['region']
            for k, v in curdata[key][section].iteritems():
                if k in row:
                    curdata[key][section][k] = row[k]
    save_species_refval(curdata)


@importer.command
def species_methods_from_csv(filename):
    curdata = load_species_refval()
    with open(filename, 'rb') as f:
        reader = UnicodeDictReader(f)
        for row in reader:
            code = row.pop('code')
            for region in REGIONS:
                key = code + '-' + region
                if not key in curdata:
                    continue
                for k, v in row.iteritems():
                    section, field = k.split('-')
                    curdata[key][section][field] = v
    save_species_refval(curdata)


@importer.command
def clean_db_refvals():
    RefValue.query.delete()
    db.session.commit()
