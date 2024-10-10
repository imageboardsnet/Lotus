import os
import requests
import json
from urllib.parse import urlparse

def faveicon_exists(url):
    ROOT_DIR = os.path.abspath(os.curdir)
    favicon_path = os.path.join(ROOT_DIR, 'static', 'favicons', url + '.ico')
    return os.path.isfile(favicon_path)

def get_imageboards(boards_json_url):
    response = requests.get(boards_json_url)
    imageboards = json.loads(response.text)
    for imageboard in imageboards:
        if 'url' in imageboard:
            parsed_url = urlparse(imageboard['url'])
            if not faveicon_exists(parsed_url.netloc):
                imageboard['favicon'] = "none"
            else:
                imageboard['favicon'] = parsed_url.netloc
    return imageboards

def get_ibpage(imageboards, start):
    ib_page = []
    for imageboard in imageboards[start:start+30]:
        ib_page.append(imageboard)
    return ib_page

def available_languages(imageboards):
    languages = []
    for imageboard in imageboards:
        if 'language' in imageboard:
            if isinstance(imageboard['language'], list):
                for lang in imageboard['language']:
                    if lang not in languages:
                        languages.append(lang)
            else:
                lang = imageboard['language']
                if lang not in languages:
                    languages.append(lang)
    return languages

def available_softwares(imageboards):
    softwares = []
    for imageboard in imageboards:
        if 'software' in imageboard:
            if isinstance(imageboard['software'], list):
                for soft in imageboard['software']:
                    if soft not in softwares:
                        if soft != "":
                            softwares.append(soft)
            else:
                soft = imageboard['software']
                if soft not in softwares:
                    if soft != "":
                        softwares.append(soft)
    return softwares

def search_imageboards(imageboards, language, software, keyword):
    search_result = []
    ksearch_result = []
    for imageboard in imageboards:
        if 'language' in imageboard and 'software' in imageboard:
            if language and software:
                if language in imageboard['language'] and software in imageboard['software']:
                    search_result.append(imageboard)
            elif language:
                if language in imageboard['language']:
                    search_result.append(imageboard)
            elif software:
                if software in imageboard['software']:
                    search_result.append(imageboard)
            elif not language and not software:
                search_result.append(imageboard)
    if keyword:
        for imageboard in search_result:
            if keyword.lower() in imageboard['name'].lower() or keyword.lower() in imageboard['description'].lower() or any(keyword.lower() in board.lower() for board in imageboard['boards']):
                ksearch_result.append(imageboard)
        return ksearch_result
    return search_result

def categorize(item):
    if item['boards'] and item['description']:
        return (1, item['name'].lower())
    elif item['description']:
        return (2, item['name'].lower())
    elif item['boards']:
        return (3, item['name'].lower())
    else:
        return (4, item['name'].lower())

def sort_imageboards(imageboards):
    imageboards = sorted(imageboards, key=categorize)
    return imageboards