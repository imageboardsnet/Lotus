from flask import Flask, render_template, request, send_from_directory
import os
import threading
import schedule
import time
import ibrender
import ibutils

app = Flask(__name__)

boards_json_url = "https://imageboardsnet.github.io/imageboards.json/imageboards.json"

def update_ib():
    global imageboards
    imageboards = ibutils.get_imageboards(boards_json_url)
    global languages
    languages = ibutils.available_languages(imageboards)
    global softwares
    softwares = ibutils.available_softwares(imageboards)
    global ibpages
    ibpages = ibrender.render_ibpages(imageboards)
    global search_render
    search_render = ibrender.render_search(languages, softwares)


def schedule_run():
    while True:
        schedule.run_pending()
        time.sleep(1)

schedule.every(30).minutes.do(update_ib)


@app.route('/')
def home():
    return ibrender.render_main( ibpages, languages, softwares, 0)

@app.route('/<int:page>')
def home_page(page):
    return ibrender.render_main(ibpages, languages, softwares, page - 1)

@app.route('/search' , methods=['POST'])
def search():
    selected_languages = request.form.getlist('language')
    selected_softwares = request.form.getlist('software')
    search_result = []
    for imageboard in imageboards:
        if 'language' in imageboard and 'software' in imageboard:
            if isinstance(imageboard['language'], list):
                for lang in selected_languages:
                    if lang in imageboard['language']:
                        search_result.append(imageboard)
                        break
            else:
                if imageboard['language'] in selected_languages:
                    search_result.append(imageboard)
            if isinstance(imageboard['software'], list):
                for soft in selected_softwares:
                    if soft in imageboard['software']:
                        search_result.append(imageboard)
                        break
            else:
                if imageboard['software'] in selected_softwares:
                    search_result.append(imageboard)

    search_result = ibrender.render_boards(search_result)
    search_render = render_template('search.html', languages=languages, softwares=softwares)
    return render_template('index.html', content= search_render + search_result, nav="1")

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
    update_ib()
    schedule_thread = threading.Thread(target=schedule_run)
    schedule_thread.start()
    app.run() 

def create_app():
    update_ib()
    schedule_thread = threading.Thread(target=schedule_run)
    schedule_thread.start()
    return app