from flask import Flask, render_template, request, send_from_directory
import os

app = Flask(__name__)

boards_json_url = "https://imageboardsnet.github.io/imageboards.json/imageboards.json"

def get_imageboards():
    import requests
    import json
    response = requests.get(boards_json_url)
    imageboards = json.loads(response.text)
    return imageboards

def render_template_outside_of_view():
    with app.app_context():
        rendered_template = render_template('boards.html', imageboards=imageboards)
        return rendered_template

imageboards = get_imageboards()

imageboards_prerendered = render_template_outside_of_view()

@app.route('/')
def home():
    search_content = render_template('search.html')
    return render_template('index.html', content=search_content + imageboards_prerendered, nav=1)

@app.route('/myboardhere')
def myboardhere():
    myboardhere_content = render_template('myboardhere.html')
    return render_template('index.html', content=myboardhere_content, nav=2)

@app.route('/about/')
def about():
    about_content = render_template('about.html')
    return render_template('index.html', content=about_content, nav=3)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    app.run()