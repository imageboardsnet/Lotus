# Lotus

imageboards.net directory built with Flask and Bootstrap 5. Pages are rendered server-side with limited client-side JavaScript.

## Quick start

Clone:

```
git clone https://github.com/imageboardsnet/Lotus.git
cd Lotus
```

Run with Docker (port 8080):

```
docker compose build
docker compose up -d
```

Run locally (port 5000):

```
pip install -r requirements.txt
python app.py
```

## Configuration

- `ENABLE_SCHEDULER`: Controls the background refresher that pulls `imageboards.json`. Defaults to on when running `python app.py`, off in WSGI. Set to `1/true/yes` to run the refresher inside your process, or leave false and trigger it externally on one worker.

## Testing

Run the test suite:

```
python -m unittest discover -s tests -v
```

## Deployment

The app expects the feed at `https://blossom.imageboards.net/imageboards.json`. If you host your own feed, set `boards_json_url` in `app.py` accordingly. For production WSGI (e.g., gunicorn), either enable the scheduler on a single worker or run the refresher out-of-process and reload the app as needed.

## Project layout

- `app.py` — Flask app, routes, scheduler hook.
- `lotus_utils.py` — data fetching, normalization, search helpers.
- `lotus_render.py` — template composition helpers.
- `templates/` and `static/` — HTML/CSS assets.
- `tests/` — unit and route tests.
- `.github/workflows/tests.yml` — CI runner for the test suite.
