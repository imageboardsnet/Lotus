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
                imageboard['cleanurl'] = "none"
            else:
                imageboard['cleanurl'] = parsed_url.netloc
    return imageboards

def get_ibpage(imageboards, start):
    ib_page = []
    for imageboard in imageboards[start:start+80]:
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
                        softwares.append(soft)
            else:
                soft = imageboard['software']
                if soft not in softwares:
                    softwares.append(soft)
    return softwares

def search_imageboards(imageboards, language, software):
    search_result = []
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
    return search_result