'''
YODA (Your Open DAta)
EU CEF Action 2019-ES-IA-0121
University of Cantabria
Developer: Johnny Choque (jchoque@tlmat.unican.es)
'''
import requests
from rdflib import Graph, URIRef


def access_url(urls):
    checked = True
    for url in urls:
        try:
            res = requests.get(url)
            if res.status_code in range(200, 399):
                checked = checked and True
            else:
                checked = checked and False
        except:
            checked = checked and False
    if checked:
        return format_result(50, 'OK. Weight assigned 50')
    else:
        return format_result(0, 'ERROR - Responded status code of HTTP HEAD request is not in the 200 or 300 range')


def download_url(urls):
    checked = True
    for url in urls:
        try:
            res = requests.get(url)
            if res.status_code in range(200, 399):
                checked = checked and True
            else:
                checked = checked and False
        except:
            checked = checked and False
    if checked:
        return format_result(50, 'OK. Weight assigned 50')
    else:
        return format_result(20, 'WARN - Property assigned but responded status code of HTTP HEAD request is not in '
                                 'the 200 or 300 range. Weight assigned to 20')


def keyword():
    return format_result(30, 'OK. The property is set. Weight assigned 30')


def theme():
    return format_result(30, 'OK. The property is set. Weight assigned 30')


def spatial():
    return format_result(20, 'OK. The property is set. Weight assigned 20')


def temporal():
    return format_result(20, 'OK. The property is set. Weight assigned 20')


def format(urls, mach_read_voc, non_prop_voc):
    mach_read_checked = True
    non_prop_checked = True
    found_checked = True
    details = 'OK. The property is set. Weight assigned 20.'
    weight = 20
    for url in urls:
        if str(url) in mach_read_voc:
            mach_read_checked = mach_read_checked and True
        else:
            mach_read_checked = mach_read_checked and False
        if str(url) in non_prop_voc:
            non_prop_checked = non_prop_checked and True
        else:
            non_prop_checked = non_prop_checked and False
        g = Graph()
        g.parse(url, format="application/rdf+xml")
        if (url, None, None) in g:
            found_checked = found_checked and True
        else:
            found_checked = found_checked and False
    if mach_read_checked:
        details += 'OK. The property is machine-readable. Weight assigned 20'
        weight = weight + 20
    else:
        details += 'ERROR. The property is not machine-readable'
    if non_prop_checked:
        details += 'OK. The property is non-proprietary. Weight assigned 20'
        weight = weight + 20
    else:
        details += 'ERROR. The property is not non-proprietary'
    if found_checked:
        details += 'OK. Found checked is True'
    else:
        details += 'ERROR. Found checked is False'
    return {'details': details, 'weight': weight}


def license(urls):
    checked = True
    for url in urls:
        g = Graph()
        g.parse(url, format="application/rdf+xml")
        if (url, None, None) in g:
            checked = checked and True
        else:
            checked = checked and False
    if checked:
        return format_result(30, 'OK. The property is set and provides the correct license information. '
                                 'Weight assigned 30')
    else:
        return format_result(20, 'OK. The property is set but the license is incorrect. Weight assigned 20')


def contact_point():
    return format_result(20, 'OK. The property is set. Weight assigned 20')


def mediatype(urls):
    checked = True
    for url in urls:
        res = requests.get(str(url))
        if res.status_code != 404:
            checked = checked and True
        else:
            checked = checked and False
    if checked:
        return format_result(20, 'OK. The property is set and correct. Weight assigned 20')
    else:
        return format_result(10, 'OK. The property is set but incorrect. Weight assigned 10')


def publisher():
    return format_result(10, 'OK. The property is set. Weight assigned 10')


def access_rights(urls):
    uri = URIRef('')
    checked = True
    is_url = True
    for url in urls:
        g = Graph()
        if type(url) != type(uri):
            is_url = False
            continue
        g.parse(url, format="application/rdf+xml")
        if (url, None, None) in g:
            checked = checked and True
        else:
            checked = checked and False
    if is_url:
        if checked:
            return format_result(15, 'OK. The property is set and uses a controlled vocabulary. Weight assigned 15')
        else:
            return format_result(10, 'OK. The property is set but the license is incorrect. Weight assigned 10')
    else:
        return format_result(10, 'OK. The property is set but does not use a valid URL. Weight assigned 10')


def issued():
    return format_result(5, 'OK. The property is set. Weight assigned 5')


def modified():
    return format_result(5, 'OK. The property is set. Weight assigned 5')


def rights():
    return format_result(5, 'OK. The property is set. Weight assigned 5')


def byte_size():
    return format_result(5, 'OK. The property is set. Weight assigned 5')


def format_result(weight, details):
    return {
        'weight': weight,
        'details': details
    }
