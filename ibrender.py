from flask import Flask, render_template

app = Flask(__name__)

def render_boards(imageboards, page):
    with app.app_context():
        imageboards = imageboards[page*10:page*10+10]
        rendered_template = render_template('boards.html', imageboards=imageboards)
    return rendered_template

def render_search(languages, softwares):
    with app.app_context():
        rendered_template = render_template('search.html', languages=languages, softwares=softwares)
    return rendered_template

def render_main(ibpage, languages, softwares, page=0):
    with app.app_context():
        search_render = render_template('search.html', languages=languages, softwares=softwares)
        pagination = render_template('page.html', length=len(ibpage))
        return render_template('index.html', content= search_render + ibpage[page] + pagination, nav="1")

