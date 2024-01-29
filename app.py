from flask import Flask, render_template, request, send_from_directory
import os
import requests
import json
import schedule
import time
import threading

app = Flask(__name__)

boards_json_url = "https://imageboardsnet.github.io/imageboards.json/imageboards.json"

def get_imageboards():
    response = requests.get(boards_json_url)
    imageboards = json.loads(response.text)
    return imageboards

def render_template_outside_of_view():
    with app.app_context():
        rendered_template = render_template('boards.html', imageboards=imageboards)
        return rendered_template

def update_imageboards():
    global imageboards
    imageboards = get_imageboards()

def update_imageboards_prerendered():
    global imageboards_prerendered
    imageboards_prerendered = render_template_outside_of_view()

schedule.every(30).minutes.do(update_imageboards)
schedule.every(30).minutes.do(update_imageboards_prerendered)

def schedule_run():
    while True:
        schedule.run_pending()
        time.sleep(1)

@app.route('/')
def home():
    search_content = render_template('search.html')
    return render_template('index.html', content=search_content + imageboards_prerendered, nav=1)

@app.route('/myboard')
def myboard():
    myboard_content = render_template('myboard.html')
    return render_template('index.html', content=myboard_content, nav=2)

@app.route('/about')
def about():
    about_content = render_template('about.html')
    return render_template('index.html', content=about_content, nav=3)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

""" if __name__ == '__main__':
    update_imageboards()
    update_imageboards_prerendered()
    schedule_thread = threading.Thread(target=schedule_run)
    schedule_thread.start()
    app.run() """

def create_app():
    update_imageboards()
    update_imageboards_prerendered()
    schedule_thread = threading.Thread(target=schedule_run)
    schedule_thread.start()
    return app