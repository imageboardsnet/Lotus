from flask import Flask, render_template, request, send_from_directory, redirect
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
    if len(ibpages) < page: return redirect('/')
    return ibrender.render_main(ibpages, languages, softwares, page - 1)

@app.route('/search' , methods=['POST'])
def search():
    language = request.form.get('language')
    software = request.form.get('software')
    if not language and not software : return redirect('/')
    search_result = ibutils.search_imageboards(imageboards, language, software)
    search_result = ibrender.render_boards(search_result)
    search_render = render_template('search.html', languages=languages, softwares=softwares, search_language=language, search_software=software)
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
    return send_from_directory(os.path.join(app.root_path, 'static'),'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.errorhandler(404)
def page_not_found(e):
    return ibrender.render_404()

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