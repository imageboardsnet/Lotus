from flask import Flask, render_template
from lotus_strings import main_title, nothing_title, main_description, nothing_description
import lotus_utils

app = Flask(__name__)

@app.template_filter('lang_flag')
def lang_flag(code):
    return lotus_utils.flag_from_code(code)

def render_boards(ib_page):
    with app.app_context():
        rendered_template = render_template('boards.html', imageboards=ib_page)
    return rendered_template

def render_ibpage(imageboards,page):
    ibpages = ""
    with app.app_context():
        ibpages = render_template('boards.html', imageboards=lotus_utils.get_ibpage(imageboards, page))
    return ibpages

def render_ibpages(imageboards):
    ibpages = []
    for i in range(0, len(imageboards), 30):
        ibpages.append(render_ibpage(imageboards, i))
    return ibpages

def render_search(
    languages,
    softwares,
    search_language=None,
    search_software=None,
    search_keyword=None,
    search_has_boards=False,
    search_has_description=False,
    search_sort="recommended",
    results_count=None,
    active_filters=None,
):
    with app.app_context():
        rendered_template = render_template(
            'search.html',
            languages=languages,
            softwares=softwares,
            search_language=search_language,
            search_software=search_software,
            search_keyword=search_keyword,
            search_has_boards=search_has_boards,
            search_has_description=search_has_description,
            search_sort=search_sort,
            results_count=results_count,
            active_filters=active_filters or []
        )
    return rendered_template

def render_stats(total_boards, total_languages, total_softwares, last_updated=None):
    with app.app_context():
        rendered_template = render_template(
            'stats.html',
            total_boards=total_boards,
            total_languages=total_languages,
            total_softwares=total_softwares,
            last_updated=last_updated,
        )
    return rendered_template

def render_main(ibpages, languages, softwares, total_boards, last_updated, page=0):
    # Pre-render the search box once so it can be reused with different content blocks.
    search_render = render_search(
        languages,
        softwares,
        search_language=None,
        search_software=None,
        search_keyword=None,
        search_sort="recommended",
        search_has_boards=False,
        search_has_description=False,
        active_filters=[],
        results_count=None
    )
    with app.app_context():
        if not ibpages:
            empty_render = render_template('nothing.html')
            return render_template(
                'index.html',
                content= search_render + empty_render,
                title=main_title,
                description=main_description
            )
        if page >= len(ibpages):
            page = 0
        pagination_bottom = render_template('page.html', page=page, length=len(ibpages))
        if page == 0:
            # First page shows stats plus search results.
            stats_render = render_template(
                'stats.html',
                total_boards=total_boards,
                total_languages=len(languages),
                total_softwares=len(softwares),
                last_updated=last_updated,
            )
            return render_template(
                'index.html',
                content= stats_render + search_render + ibpages[page] + pagination_bottom,
                title=main_title,
                description=main_description
            )
        else:
            return render_template(
                'index.html',
                content= search_render + ibpages[page] + pagination_bottom,
                title=main_title + " [page " + str(page+1) +"]" ,
                description=main_description
            )

def render_404():
    with app.app_context():
        notfound_render = render_template('404.html')
        return render_template('index.html', content=notfound_render, title=nothing_title, description=nothing_description)
    
def render_nothing():
    with app.app_context():
        nothing_render = render_template('nothing.html')
        return render_template('index.html', content=nothing_render, title=nothing_title, description=nothing_description)
