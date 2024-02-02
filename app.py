from flask import Flask, render_template, request, send_from_directory
import os
import requests
import json
import schedule
import time
import threading
import mimetypes
from urllib.parse import urlparse


app = Flask(__name__)

boards_json_url = "https://imageboardsnet.github.io/imageboards.json/imageboards.json"

def get_imageboards():
    response = requests.get(boards_json_url)
    imageboards = json.loads(response.text)
    for imageboard in imageboards:
        if 'url' in imageboard:
            parsed_url = urlparse(imageboard['url'])
            imageboard['cleanurl'] = parsed_url.netloc
    return imageboards

def render_boards():
    with app.app_context():
        rendered_template = render_template('boards.html', imageboards=imageboards)
        return rendered_template
    
def available_languages():
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

def available_software():
    software = []
    for imageboard in imageboards:
        if 'software' in imageboard:
            if isinstance(imageboard['software'], list):
                for soft in imageboard['software']:
                    if soft not in software:
                        software.append(soft)
            else:
                soft = imageboard['software']
                if soft not in software:
                    software.append(soft)
    return software

def render_search():
    with app.app_context():
        rendered_template = render_template('search.html', languages=languages, softwares=software)
        return rendered_template

def update_imageboards():
    global imageboards
    imageboards = get_imageboards()
    global languages
    languages = available_languages()
    global software
    software = available_software()

def update_rendered():
    global imageboards_prerendered
    imageboards_prerendered = render_boards()
    global search_prerendered
    search_prerendered = render_search()


schedule.every(30).minutes.do(update_imageboards)
schedule.every(30).minutes.do(update_rendered)

def schedule_run():
    while True:
        schedule.run_pending()
        time.sleep(1)

@app.route('/')
def home():
    
    return render_template('index.html', content= search_prerendered + imageboards_prerendered, nav="1")

@app.route('/myboard')
def myboard():
    myboard_content = render_template('myboard.html')
    return render_template('index.html', content=myboard_content, nav="2")

@app.route('/about')
def about():
    about_content = render_template('about.html')
    return render_template('index.html', content=about_content, nav="3")

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    update_imageboards()
    update_rendered()
    schedule_thread = threading.Thread(target=schedule_run)
    schedule_thread.start()
    app.run() 

def create_app():
    update_imageboards()
    update_rendered()
    schedule_thread = threading.Thread(target=schedule_run)
    schedule_thread.start()
    return app