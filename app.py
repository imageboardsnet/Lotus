from flask import Flask, render_template, request, send_from_directory
import os
import requests
import json
from urllib.parse import urlparse

app = Flask(__name__)

boards_json_url = "https://imageboardsnet.github.io/imageboards.json/imageboards.json"

def faveicon_exists(url):
    favicon_path = os.path.join(app.root_path, 'static', 'favicons', url + '.ico')
    return os.path.isfile(favicon_path)

def get_imageboards():
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

def render_boards(imageboards,page):
    imageboards = imageboards[page*10:page*10+10]
    rendered_template = render_template('boards.html', imageboards=imageboards)
    return rendered_template
    
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

def available_software(imageboards):
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

def render_main(page=0):
    imageboards = get_imageboards()
    languages = available_languages(imageboards)
    software = available_software(imageboards)
    search_render = render_template('search.html', languages=languages, software=software)
    ib_render = render_boards(imageboards,page)
    page = render_template('page.html', page=page)
    return render_template('index.html', content= search_render + ib_render + page, nav="1")

@app.route('/')
def home():
    return render_main()

@app.route('/<int:page>')
def home_page(page):
    return render_main(page)

@app.route('/search', methods=['POST'])
def search():
    imageboards = get_imageboards()
    languages = available_languages(imageboards)
    software = available_software(imageboards)
    search_prerendered = render_template('search.html', languages=languages, software=software)
    search = request.form['search']
    language = request.form['language']
    software = request.form['software']
    filtered_boards = []
    for imageboard in imageboards:
        if search.lower() in imageboard['name'].lower() or search.lower() in imageboard['description'].lower():
            if language != "all":
                if isinstance(imageboard['language'], list):
                    if language in imageboard['language']:
                        filtered_boards.append(imageboard)
                else:
                    if language == imageboard['language']:
                        filtered_boards.append(imageboard)
            else:
                filtered_boards.append(imageboard)
    imageboards_prerendered = render_boards(filtered_boards,0)
    return render_template('index.html', content=search_prerendered + imageboards_prerendered, nav="1")

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
    app.run() 

def create_app():
    return app