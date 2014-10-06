from datetime import datetime

from BeautifulSoup import BeautifulSoup
from flask import current_app
import requests

from art17.aggregation import aggregation_manager
from art17.models import (
    Dataset, db, DataHabitatsCheckList, DataSpeciesCheckList,
    LuHdSpecies, LuHabitattypeCodes)


REGION_MAP = {
    'Panonica': 'PAN',
    'Alpina': 'ALP',
    'Continentala': 'CON',
    'Stepica': 'STE',
    'Mediteraneana': 'MED',
    'Boreala': 'BOR',
    'Marea Neagra': 'MBLS',
    'Pontic': 'BLS',
}

PRESENCE_MAP = {
    'Prezent': '1',
    'Rezerva stiintifica': 'SR',
    'Reintrodus': '1',
    'Extinct': 'EXB',
    'Extinct in salbaticie': 'EXB',
    'Marginal': 'MAR',
}


def yn(bool_value):
    return 'Y' if bool_value else 'N'


def create_checklist():
    species_endpoint = current_app.config.get(
        'OID_SPECIES',
        'http://natura.anpm.ro/api/CNSERVICE.svc/ListaVerificareSpecii',
    )
    habitats_endpoint = current_app.config.get(
        'OID_HABITATS',
        'http://natura.anpm.ro/api/CNSERVICE.svc/ListaVerificareHabitate',
    )
    dataset = Dataset(
        preview=True, checklist=True, date=datetime.today(),
        year_start=current_app.config.get('DEFAULT_YEAR_START'),
        year_end=current_app.config.get('DEFAULT_YEAR_END'),
        comment=str(datetime.now()),
    )
    db.session.add(dataset)
    db.session.commit()

    response = requests.get(species_endpoint)
    species = species_from_oid(response.content, dataset)

    response = requests.get(habitats_endpoint)
    habitats = habitats_from_oid(response.content, dataset)

    for o in species + habitats:
        db.session.add(o)
    db.session.commit()


def habitats_from_oid(data, dataset):
    b = BeautifulSoup(data)
    entries = b.findAll("entry")

    habitats = []
    for e in entries:
        cod = e.content.findAll("d:codhabitat")[0].text
        name = e.content.findAll("d:numehabitat")[0].text
        region = e.content.findAll("d:bioregiune")[0].text
        presence = e.content.findAll("d:statusverificare")[0].text
        guid = e.content.findAll("d:id")[0].text
        priority = e.content.findAll("d:prioritatehabitat")[0].text == "true"
        if region not in REGION_MAP:
            raise ValueError('Unknown region: ' + region)
        region = REGION_MAP[region]
        if presence not in PRESENCE_MAP:
            raise ValueError('Unknown presence: ' + presence)
        presence = PRESENCE_MAP[presence]
        data = {
            'code': cod, 'name': name, 'bio_region': region,
            'presence': presence, 'globalid': guid,
            'member_state': 'RO',
            'priority': '1' if priority else '',
        }
        if dataset:
            data['dataset_id'] = dataset.id
            habitats.append(DataHabitatsCheckList(**data))
        else:
            habitats.append(data)
    return habitats


def species_from_oid(data, dataset):
    b = BeautifulSoup(data)
    entries = b.findAll("entry")

    species = []
    for e in entries:
        cod_specie = e.content.findAll("d:codspecie")[0].text
        name = e.content.findAll("d:denumirestiintifica")[0].text
        region = e.content.findAll("d:bioregiune")[0].text
        presence = e.content.findAll("d:statusverificare")[0].text
        guid = e.content.findAll("d:id")[0].text
        if e.content.findAll("d:dh1"):
            dh1 = e.content.findAll("d:dh1")[0].text == "true"
            dh2 = e.content.findAll("d:dh2")[0].text == "true"
            dh4 = e.content.findAll("d:dh4")[0].text == "true"
            dh5 = e.content.findAll("d:dh5")[0].text == "true"
        else:
            raise ValueError('Missing dh')
        priority = e.content.findAll("d:prioritatespecie")[0].text == "true"
        if region not in REGION_MAP:
            raise ValueError('Unknown region: ' + region)
        region = REGION_MAP[region]
        if presence not in PRESENCE_MAP:
            raise ValueError('Unknown presence: ' + presence)
        presence = PRESENCE_MAP[presence]
        data = {
            'code': cod_specie, 'name': name, 'bio_region': region,
            'presence': presence, 'globalid': guid,
            'hd_name': name,
            'member_state': 'RO',
            'priority': '1' if priority else '',
            'annex_ii': yn(dh2), 'annex_iv': yn(dh4), 'annex_v': yn(dh5),
        }
        if dataset:
            data['dataset_id'] = dataset.id
            species.append(DataSpeciesCheckList(**data))
        else:
            species.append(data)
    return species


@aggregation_manager.command
def checklist():
    with open('misc/ListaVerificareHabitate.xml') as fin:
        habitats = habitats_from_oid(fin, None)
        print "Habitat:", habitats[0] if habitats else '-'
    with open('misc/ListaVerificareSpecii.xml') as fin:
        species = species_from_oid(fin, None)
        print "Specie:", species[0] if species else '-'


@aggregation_manager.command
def fix_checklist():
    print("Fix initial checklist with data from adiacent tables.")
    print("Species...")
    hd_map = dict(LuHdSpecies.query.with_entities(LuHdSpecies.code,
                                                  LuHdSpecies.annexpriority))
    for sc in DataSpeciesCheckList.query.filter_by(dataset_id=None):
        sc.priority = str(hd_map.get(sc.natura_2000_code, ''))

    hd_map = dict(
        LuHabitattypeCodes.query.with_entities(LuHabitattypeCodes.code,
                                               LuHabitattypeCodes.priority)
    )
    print("Habitats...")
    for hb in DataHabitatsCheckList.query.filter_by(dataset_id=None):
        hb.priority = str(hd_map.get(hb.natura_2000_code, ''))
    print("Commit")
    db.session.commit()