from flask import Flask, render_template, request, send_from_directory, redirect, url_for, has_request_context
from flask_sitemapper import Sitemapper
from lotus_strings import search_title, about_title, search_description, about_description
import os
import threading
import schedule
import time
from datetime import datetime
import lotus_render
import lotus_utils

sitemapper = Sitemapper()

app = Flask(__name__)
sitemapper.init_app(app)

boards_json_url = "https://blossom.imageboards.net/imageboards.json"
last_updated = None
state_lock = threading.Lock()  # Protects shared in-memory state.
imageboards = []
languages = []
softwares = []
ibpages = []
search_render = ""
schedule_thread = None

def should_run_scheduler(default=False):
    """Gate the background refresh thread based on ENABLE_SCHEDULER."""
    env_value = os.getenv("ENABLE_SCHEDULER")
    if env_value is None:
        return default
    return env_value.lower() not in ("0", "false", "no")

@app.template_filter('lang_flag')
def lang_flag(code):
    return lotus_utils.flag_from_code(code)

@app.context_processor
def inject_seo_defaults():
    """Provide canonical URLs and social defaults to all templates."""
    if has_request_context():
        base_url = request.url_root.rstrip("/")
        canonical_url = request.base_url
        social_image = url_for('static', filename='img/social-card.png', _external=True)
    else:
        base_url = "https://imageboards.net"
        canonical_url = base_url
        social_image = "/static/img/social-card.png"
    return {
        "canonical_url": canonical_url,
        "site_name": "ImageBoards.net",
        "social_image": social_image,
        "og_type": "website",
        "base_url": base_url,
        "robots_directive": "index, follow",
    }

def update_ib():
    global imageboards, languages, softwares, ibpages, search_render, last_updated
    try:
        new_imageboards = lotus_utils.get_imageboards(boards_json_url)
    except Exception as exc:
        print(f"[update_ib] Failed to refresh imageboards: {exc}")
        return

    with state_lock:
        # Compute derived state in one lock to keep routes consistent.
        imageboards = lotus_utils.sort_imageboards(new_imageboards)
        languages = lotus_utils.available_languages(imageboards)
        softwares = lotus_utils.available_softwares(imageboards)
        ibpages = lotus_render.render_ibpages(imageboards)
        search_render = lotus_render.render_search(languages, softwares)
        last_updated = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

def schedule_run():
    """Run scheduled jobs forever in a daemon thread."""
    while True:
        schedule.run_pending()
        time.sleep(1)

schedule.every(30).minutes.do(update_ib)

def ensure_scheduler():
    """Start scheduler once; safe to call repeatedly."""
    global schedule_thread
    if schedule_thread and schedule_thread.is_alive():
        return
    schedule_thread = threading.Thread(target=schedule_run, daemon=True)
    schedule_thread.start()

@sitemapper.include()
@app.route('/')
def home():
    return lotus_render.render_main(ibpages, languages, softwares, len(imageboards), last_updated, 0)

@sitemapper.include(url_variables={"page": list(range(2, 51))},)
@app.route('/page/<int:page>')
def home_page(page):
    if len(ibpages) < page: return redirect('/')
    if page == 1 : return redirect('/')
    return lotus_render.render_main(ibpages, languages, softwares, len(imageboards), last_updated, page - 1)

@app.route('/search' , methods=['POST'])
def search():
    language = request.form.get('language')
    software = request.form.get('software')
    keyword = request.form.get('keyword')
    has_boards = request.form.get('has_boards') == 'on'
    has_description = request.form.get('has_description') == 'on'
    sort_by = request.form.get('sort_by', 'recommended')
    if not language and not software and not keyword and not has_boards and not has_description and sort_by == 'recommended':
        return redirect('/')
    search_result = lotus_utils.search_imageboards(
        imageboards,
        language,
        software,
        keyword,
        has_boards=has_boards,
        has_description=has_description,
        sort_by=sort_by
    )
    active_filters = []
    if language: active_filters.append(f"Language: {language}")
    if software: active_filters.append(f"Software: {software}")
    if keyword: active_filters.append(f"Keyword: {keyword}")
    if has_boards: active_filters.append("Has board list")
    if has_description: active_filters.append("Has description")
    if sort_by and sort_by != 'recommended': active_filters.append(f"Sorted by: {sort_by}")
    search_resultr = lotus_render.render_boards(search_result)
    search_render = lotus_render.render_search(
        languages,
        softwares,
        search_language=language,
        search_software=software,
        search_keyword=keyword,
        search_has_boards=has_boards,
        search_has_description=has_description,
        search_sort=sort_by,
        results_count=len(search_result),
        active_filters=active_filters
    )
    if not search_result :
        nothing_render = render_template('nothing.html')
        return render_template(
            'index.html',
            content= search_render + nothing_render,
            title=search_title,
            description=search_description,
            robots_directive="noindex, follow"
        )
    return render_template(
        'index.html',
        content= search_render + search_resultr,
        title=search_title,
        description=search_description,
        robots_directive="noindex, follow"
    )

@sitemapper.include()
@app.route('/lucky', methods=['GET', 'POST'])
def lucky():
    import random
    if request.method == 'POST':
        chosen = random.sample(imageboards, 3)
        lootbox = render_template('lucky.html', opened=True, imageboards=chosen)
        return render_template('index.html', content=lootbox, title='The Lucky Box™', description='You got a lucky imageboard!')
    lootbox = render_template('lucky.html', opened=False, imb=None)
    return render_template('index.html', content=lootbox, title='The Lucky Box™', description='Click to get a random imageboard!')

@sitemapper.include()
@app.route('/about')
def about():
    about_content = render_template('about.html')
    return render_template('index.html', content=about_content, title=about_title,description=about_description)

@app.route('/viewer')
def viewer():
    board_id = request.args.get('id')
    selected_board = None
    for imb in imageboards:
        if board_id and str(imb.get('id')) == str(board_id):
            selected_board = imb
            break
    if not selected_board and len(imageboards) > 0:
        selected_board = imageboards[0]
    viewer_content = render_template('viewer.html', imageboards=imageboards, selected_board=selected_board)
    return render_template('index.html', content=viewer_content, title='Inline Browser', description='Browse boards without leaving the page.')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/robots.txt')
def robots():
    return send_from_directory(os.path.join(app.root_path, 'static'),'robots.txt', mimetype='text/plain')

@app.route("/sitemap.xml")
def sitemap():
  return sitemapper.generate()

@app.errorhandler(404)
def page_not_found(e):
    return lotus_render.render_404()

if __name__ == '__main__':
    update_ib()
    if should_run_scheduler(default=True):
        ensure_scheduler()
    app.run() 

def create_app():
    update_ib()
    if should_run_scheduler():
        ensure_scheduler()
    return app
