import os
import requests
from urllib.parse import urlparse


def favicon_exists(url):
    """Check for a pre-downloaded favicon under static/favicons."""
    root_dir = os.path.abspath(os.curdir)
    favicon_path = os.path.join(root_dir, 'static', 'favicons', f"{url}.ico")
    return os.path.isfile(favicon_path)


def flag_from_code(code):
    if not code:
        return '🏳️'
    code = str(code)
    special = {
        'en': '🇬🇧',
        'es': '🇪🇸',
        'pt': '🇵🇹',
        'zh': '🇨🇳',
        'ja': '🇯🇵',
        'ko': '🇰🇷',
        'ru': '🇷🇺',
        'uk': '🇺🇦',
        'be': '🇧🇾',
        'ar': '🇸🇦',
        'sv': '🇸🇪',
        'hi': '🇮🇳',
        'fr': '🇫🇷',
        'de': '🇩🇪',
        'pl': '🇵🇱',
        'it': '🇮🇹',
        'nl': '🇳🇱',
        'tr': '🇹🇷',
        'cs': '🇨🇿',
        'fi': '🇫🇮',
        'no': '🇳🇴',
        'da': '🇩🇰',
        'bg': '🇧🇬',
        'hu': '🇭🇺',
        'he': '🇮🇱',
        'iw': '🇮🇱',
        'id': '🇮🇩',
        'ms': '🇲🇾',
        'th': '🇹🇭',
        'vi': '🇻🇳',
        'fa': '🇮🇷',
        'ro': '🇷🇴',
        'el': '🇬🇷',
        'sk': '🇸🇰',
        'sl': '🇸🇮',
        'sr': '🇷🇸',
        'hr': '🇭🇷',
        'lt': '🇱🇹',
        'lv': '🇱🇻',
        'et': '🇪🇪',
        'bn': '🇧🇩',
        'ta': '🇮🇳',
        'ur': '🇵🇰',
        'sw': '🇰🇪',
        'af': '🇿🇦',
        'ca': '🇪🇸',
        'gl': '🇪🇸',
    }
    normalized = code.lower()
    if normalized in special:
        return special[normalized]
    if '-' in normalized:
        parts = normalized.split('-')
        for p in reversed(parts):
            if len(p) == 2 and p.isalpha():
                normalized = p
                break
    if len(normalized) == 2 and normalized.isalpha():
        offset = ord('A')
        return chr(0x1F1E6 + ord(normalized[0].upper()) - offset) + chr(0x1F1E6 + ord(normalized[1].upper()) - offset)
    return '🏳️'


def get_imageboards(boards_json_url):
    """Download and normalize imageboard entries from the JSON feed."""
    response = requests.get(boards_json_url, timeout=10)
    response.raise_for_status()
    imageboards = response.json()

    def normalize_list_field(value):
        if isinstance(value, list):
            return [v for v in value if v]
        if value:
            return [value]
        return []

    normalized = []
    for imageboard in imageboards:
        if 'url' in imageboard:
            parsed_url = urlparse(imageboard['url'])
            if not favicon_exists(parsed_url.netloc):
                imageboard['favicon'] = "none"
            else:
                imageboard['favicon'] = parsed_url.netloc

        imageboard['language'] = normalize_list_field(imageboard.get('language'))
        imageboard['software'] = normalize_list_field(imageboard.get('software'))
        imageboard['boards'] = imageboard.get('boards') if isinstance(imageboard.get('boards'), list) else []

        normalized.append(imageboard)
    return normalized


def get_ibpage(imageboards, start):
    """Return one 30-item page slice."""
    return imageboards[start:start + 30]


def available_languages(imageboards):
    return _collect_unique_field(imageboards, 'language')


def available_softwares(imageboards):
    return _collect_unique_field(imageboards, 'software')


def _collect_unique_field(imageboards, field_name):
    """Collect unique values for a list field while preserving order."""
    seen = set()
    values = []
    for imageboard in imageboards:
        items = imageboard.get(field_name, [])
        if not isinstance(items, list):
            items = [items]
        for item in items:
            if not item or item in seen:
                continue
            seen.add(item)
            values.append(item)
    return values


def search_imageboards(imageboards, language, software, keyword, has_boards=False, has_description=False, sort_by="recommended"):
    """Filter and order imageboards according to the UI search settings."""
    filtered = []
    keyword_lower = keyword.lower() if keyword else None

    for imageboard in imageboards:
        languages = imageboard.get('language', [])
        softwares = imageboard.get('software', [])
        boards = imageboard.get('boards', []) or []
        description = imageboard.get('description', '') or ''
        name = imageboard.get('name', '')

        if language and language not in languages:
            continue
        if software and software not in softwares:
            continue

        if keyword_lower:
            matches_keyword = (
                keyword_lower in name.lower()
                or keyword_lower in description.lower()
                or any(keyword_lower in board.lower() for board in boards)
            )
            if not matches_keyword:
                continue

        if has_boards and not boards:
            continue
        if has_description and description.strip() == '':
            continue

        filtered.append(imageboard)

    if sort_by == "alphabetical":
        return sorted(filtered, key=lambda item: item.get('name', '').lower())
    if sort_by == "board_count":
        return sorted(filtered, key=lambda item: (-len(item.get('boards', []) or []), item.get('name', '').lower()))

    return sort_imageboards(filtered)

def categorize(item):
    """Sort key: prefer items with both boards and description first."""
    if item['boards'] and item['description']:
        return (1, item['name'].lower())
    elif item['description']:
        return (2, item['name'].lower())
    elif item['boards']:
        return (3, item['name'].lower())
    else:
        return (4, item['name'].lower())

def sort_imageboards(imageboards):
    imageboards = sorted(imageboards, key=categorize)
    return imageboards
