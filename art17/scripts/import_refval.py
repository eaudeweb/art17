# coding=utf-8
import os
from csv import DictReader
from art17.aggregation.refvalues import load_refval, save_refval, \
    load_species_refval, save_species_refval
from art17.scripts import importer


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


def smart_update(data, newdata):
    for key, value in data.items():
        if key not in newdata:
            print "Ignoring: ", key, "not found in new data."
            continue
        else:
            print "Updating:", key
        for group, values in value.items():
            if group in newdata[key]:
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
        data = {
            'range': {
                'Areal favorabil referinta': unicode(sr.range_surface_area),
            },
            'habitat': {
                u'Suprafața adecvata': unicode(sr.habitat_surface_area),
            },
            'population_range': {
                'Populatia favorabila de referinta': unicode(
                    sr.population_minimum_size or 0)
            }
        }
        print key, data
        return (key, data)

    newdata = dict(generic_species_exporter(format_row, dataset_id=dataset_id))
    curdata = load_species_refval()
    data = smart_update(curdata, newdata)
    save_species_refval(data)
    print "Done."
