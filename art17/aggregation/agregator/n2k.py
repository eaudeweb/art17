from flask import current_app
from urllib import urlencode
import requests

HABITAT_COVER_URL = '/Natura2000/MapServer/3'
SPECIES_COVER_URL = '/Natura2000/MapServer/26'


def generic_n2k_call(url, where_query, out_fields=""):
    url = current_app.config.get('GIS_API_URL') + url
    url += "/query?" + urlencode({
        'where': where_query,
        'outFields': out_fields,
        'f': "json",
        'returnGeometry': "false",
    })

    print "Requesting:" + url
    res = requests.get(url)
    if res.status_code == 200:
        data = res.json()
        return data.get('features')


def get_habitat_cover_range(habcode, region):
    where_query = "HABITAT_CODE='%s'" % habcode
    data = generic_n2k_call(HABITAT_COVER_URL, where_query,
                            out_fields="HABITAT_COVER")
    if not data:
        return None, None

    values = [e['attributes']['HABITAT_COVER'] for e in data]
    return min(values), max(values)


def get_species_population_range(speccode, region):
    where_query = "SPECIES_CODE='%s'" % speccode
    data = generic_n2k_call(SPECIES_COVER_URL, where_query,
                            out_fields="SPECIES_SIZE_MIN,SPECIES_SIZE_MAX")
    if not data:
        return None, None

    min_values = [
        v for v in
        (e['attributes']['SPECIES_SIZE_MIN'] for e in data)
        if v is not None
    ]

    max_values = [
        v for v in
        (e['attributes']['SPECIES_SIZE_MIN'] for e in data)
        if v is not None
    ]

    return sum(min_values) or None, sum(max_values) or None