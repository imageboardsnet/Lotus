from flask import Flask, render_template, request, send_from_directory, redirect
import os
import threading
import schedule
import time
import ibrender
import ibutils

app = Flask(__name__)

boards_json_url = "https://blossom.imageboards.net/imageboards.json"

def update_ib():
    global imageboards
    imageboards = ibutils.get_imageboards(boards_json_url)
    imageboards = ibutils.sort_imageboards(imageboards)
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
    keyword = request.form.get('keyword')
    if not language and not software and not keyword: return redirect('/')
    search_result = ibutils.search_imageboards(imageboards, language, software, keyword)
    search_resultr = ibrender.render_boards(search_result)
    search_render = render_template('search.html', languages=languages, softwares=softwares, search_language=language, search_software=software, search_keyword=keyword)
    if not search_result :
        nothing_render = render_template('nothing.html')
        return render_template('index.html', content= search_render + nothing_render)
    return render_template('index.html', content= search_render + search_resultr)

@app.route('/about')
def about():
    about_content = render_template('about.html')
    return render_template('index.html', content=about_content)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/robots.txt')
def robots():
    return send_from_directory(os.path.join(app.root_path, 'static'),'robots.txt', mimetype='text/plain')

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
