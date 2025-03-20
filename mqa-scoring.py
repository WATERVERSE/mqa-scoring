#!/usr/bin/env python3
'''
YODA (Your Open DAta)
EU CEF Action 2019-ES-IA-0121
University of Cantabria
Developer: Johnny Choque (jchoque@tlmat.unican.es)
'''
import sys

import requests
import json
from rdflib import Graph
import mqaMetrics as mqa
import os

URL_EDP = 'https://data.europa.eu/api/mqa/shacl/validation/report'
HEADERS = {'Content-Type': 'application/ld+json'}
MACH_READ_FILE = 'edp-vocabularies/edp-machine-readable-format.rdf'
NON_PROP_FILE = 'edp-vocabularies/edp-non-proprietary-format.rdf'


def other_cases(pred, objs, g):
    for obj in objs:
        met = str_metric(obj, g)
        if met is None:
            return mqa.format_result(0, 'Not included in MQA - ' + str_metric(pred, g))
        else:
            return mqa.format_result(0, 'Not included in MQA - ' + str(met))


def str_metric(val, g):
    val_str = str(val)
    for prefix, ns in g.namespaces():
        if val.find(ns) != -1:
            met_str = val_str.replace(ns, prefix + ":")
            return met_str
    return val_str


def load_edp_vocabulary(file):
    g = Graph()
    g.parse(file, format="application/rdf+xml")
    voc = []
    for sub, pred, obj in g:
        voc.append(str(sub))
    return voc


def edp_validator(dataset_entity, weight):
    print('* SHACL validation')
    try:
        r_edp = requests.post(URL_EDP, data=dataset_entity, headers=HEADERS)
        r_edp.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err, file=sys.stderr)
        print(err.response.text, file=sys.stderr)
        raise SystemExit(err)
    report = json.loads(r_edp.text)
    if val_result(report):
        print('   Result: OK. The metadata has successfully passed the EDP validator. Weight assigned 30')
        weight = weight + 30
    else:
        print('   Result: ERROR. DCAT-AP errors found in metadata')
    return weight


def val_result(d):
    if 'sh:conforms' in d:
        return d['sh:conforms']
    for k in d:
        if isinstance(d[k], list):
            for i in d[k]:
                if 'sh:conforms' in i:
                    return i['sh:conforms']


def get_metrics(g):
    metrics = {}
    for sub, pred, obj in g:
        if pred not in metrics.keys():
            metrics[pred] = None
    for pred in metrics.keys():
        obj_list = []
        for obj in g.objects(predicate=pred):
            obj_list.append(obj)
        metrics[pred] = obj_list
    return metrics


def main():
    dataset_content = json.load(sys.stdin)
    install_dir = sys.argv[1]

    g = Graph()
    g.parse(data=json.dumps(dataset_content), format="json-ld")

    mach_read_path = os.path.join(install_dir, MACH_READ_FILE)
    mach_read_voc = load_edp_vocabulary(mach_read_path)
    non_prop_path = os.path.join(install_dir, NON_PROP_FILE)
    non_prop_voc = load_edp_vocabulary(non_prop_path)

    weight = 0
    # weight = edp_validator(json.dumps(dataset_content), weight)
    # print('   Current weight =', weight)

    metrics = get_metrics(g)
    result_details = {}
    for pred in metrics.keys():
        met = str_metric(pred, g)
        objs = metrics[pred]
        # Findability
        if met == "dcat:keyword":
            result_met = mqa.keyword()
        elif met == "dcat:theme":
            result_met = mqa.theme()
        elif met == "dct:spatial":
            result_met = mqa.spatial()
        elif met == "dct:temporal":
            result_met = mqa.temporal()
        # Accessibility
        elif met == "dcat:accessURL":
            result_met = mqa.access_url(objs)
        elif met == "dcat:downloadURL":
            result_met = mqa.download_url(objs)
        # Interoperability
        elif met == "dct:format":
            result_met = mqa.format(objs, mach_read_voc, non_prop_voc)
        elif met == "dcat:mediaType":
            result_met = mqa.mediatype(objs)
        # Reusability
        elif met == "dct:license":
            result_met = mqa.license(objs)
        elif met == "dct:accessRights":
            result_met = mqa.access_rights(objs)
        elif met == "dcat:contactPoint":
            result_met = mqa.contact_point()
        elif met == "dct:publisher":
            result_met = mqa.publisher()
        # Contextuality
        elif met == "dct:issued":
            result_met = mqa.issued()
        elif met == "dct:modified":
            result_met = mqa.modified()
        elif met == "dct:rights":
            result_met = mqa.rights()
        elif met == "dcat:byteSize":
            result_met = mqa.byte_size()
        else:
            result_met = other_cases(pred, objs, g)
        result_details[met] = result_met
        weight += result_met['weight']

    findability_metadata = ["dcat:keyword", "dcat:theme", "dct:spatial", "dct:temporal"]
    accessibility_metadata = ["dcat:accessURL", "dcat:downloadURL"]
    interoperability_metadata = ["dct:format", "dcat:mediaType"]
    reusability_metadata = ["dct:license", "dct:accessRights", "dcat:contactPoint", "dct:publisher"]
    contextuality_metadata = ["dct:issued", "dct:modified", "dct:rights", "dcat:byteSize"]
    all_supported_metadata = findability_metadata + accessibility_metadata + interoperability_metadata + reusability_metadata + contextuality_metadata
    all_evaluated_metadata = list(result_details.keys())
    not_evaluated_metadata = list(set(all_supported_metadata) - set(all_evaluated_metadata))

    result = {
        'fairScore': {
            'type': 'Property',
            'value': weight,
            'details': {
                'type': 'Property',
                'value': result_details
            },
            'evaluatedMetadata': {
                'type': 'Property',
                'value': ','.join(all_evaluated_metadata)
            },
            'notEvaluatedMetadata': {
                'type': 'Property',
                'value': ','.join(not_evaluated_metadata)
            }
        }
    }
    json.dump(result, sys.stdout, indent=4)


if __name__ == "__main__":
    main()
