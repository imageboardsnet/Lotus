from flask import Flask, render_template
import ibutils

app = Flask(__name__)

def render_boards(ib_page):
    with app.app_context():
        rendered_template = render_template('boards.html', imageboards=ib_page)
    return rendered_template

def render_ibpage(imageboards,page):
    ibpages = ""
    with app.app_context():
        ibpages = render_template('boards.html', imageboards=ibutils.get_ibpage(imageboards, page))
    return ibpages

def render_ibpages(imageboards):
    ibpages = []
    for i in range(0, len(imageboards), 80):
        ibpages.append(render_ibpage(imageboards, i))
    return ibpages

def render_search(languages, softwares):
    with app.app_context():
        rendered_template = render_template('search.html', languages=languages, softwares=softwares)
    return rendered_template

def render_main(ibpages, languages, softwares, page=0):
    with app.app_context():
        search_render = render_template('search.html', languages=languages, softwares=softwares)
        pagination = render_template('page.html',page=page, length=len(ibpages))
        return render_template('index.html', content= search_render + ibpages[page] + pagination)

def render_404():
    with app.app_context():
        notfound_render = render_template('404.html')
        return render_template('index.html', content=notfound_render)