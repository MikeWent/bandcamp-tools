#!/usr/bin/env python3

from collections import namedtuple
import json
import re

from bs4 import BeautifulSoup
import requests
import js2py

# HTML parser
# See bs4 documentation: https://www.crummy.com/software/BeautifulSoup/bs4/doc/#installing-a-parser
# Default is "lxml"
HTML_PARSER = "lxml"

# Precompile regex
RE_TRALBUMDATA = re.compile(r'(var\s*TralbumData\s*=\s*{.*?};)', re.IGNORECASE | re.DOTALL | re.MULTILINE)
RE_JS_VAR_NAME = re.compile(r'var\s*(\w+)\s*')

# Data structures
Album = namedtuple("Album", ["title", "artist", "url"])
Track = namedtuple("Track", ["title", "artist", "album", "url", "duration"])

##
# Private functions
##

def _js_array_to_python_array(js_source_code):
    """Convert JS array create statement into Python object

    Params:
        js_source_code - JavaScript variable definition code,
                         for example "var smth = {'foo': 123, 'bar': 456}"

    Returns:
        Python dict
    """
    array_name = RE_JS_VAR_NAME.findall(js_source_code)[0]
    js_source_code = "function a() {\n"+js_source_code
    js_source_code += "\nreturn JSON.stringify("+array_name+");}\na();"
    js_array_as_json = js2py.eval_js(js_source_code)
    python_array = json.loads(js_array_as_json)
    return python_array


def _http_get(*args, **kwargs):
    """Make HTTP GET request with some defined cookies

    Params:
        all 'requests.get' params

    Returns:
        see 'requests.get' docs
    """
    return requests.get(*args, cookies={
        # load mobile version instead of desktop site
        "mvp": "p"
    }, **kwargs)


##
# Public functions
##

def get_raw_info(url):
    """Get raw information about track/album by URL

    Params:
        url - URL of an album/track

    Returns:
        non-documented dict with a lot of information
    """
    html = _http_get(url).text
    js_array_with_info = RE_TRALBUMDATA.findall(html)[0]
    return _js_array_to_python_array(js_array_with_info)


def get_album(url):
    """Get album information from URL

    Params:
        url - URL of an album

    Returns:
        Album object
    """
    raw_album_info = get_raw_info(url)
    return Album(
        title=raw_album_info["current"]["title"],
        artist=raw_album_info["artist"],
        url=url
    )


def get_track(url):
    """Get track information from URL

    Params:
        url - URL of a track

    Returns:
        Track object
    """
    raw_track_info = get_raw_info(url)
    if len(raw_track_info["trackinfo"]) < 1:
        return None
    album_url = url[:url.find("/track/")]+raw_track_info["album_url"]
    album = get_album(album_url)
    return Track(
        title=raw_track_info["current"]["title"],
        artist=raw_track_info["artist"],
        album=album,
        url=raw_track_info["trackinfo"][0]["file"]["mp3-128"],
        duration=raw_track_info["trackinfo"][0]["duration"]
    )


def get_album_tracklist(album):
    """Get list of Track objects by an album URL or an Album object

    Params:
        album - Bandcamp album URL or an Album object

    Returns:
        list of Track objects
    """
    if isinstance(album, Album):
        # just use as is
        current_album = album
        raw_album_info = get_raw_info(album.url)
    elif isinstance(album, str):
        # generate Album object from URL
        current_album = get_album(album)
        raw_album_info = get_raw_info(album)
    tracks = []
    for track in raw_album_info["trackinfo"]:
        if not track.get("file") or not track.get("duration"):
            continue  # skip undownloadable tracks
        tracks.append(
            Track(
                title=track["title"],
                artist=current_album.artist,
                album=current_album,
                url=track["file"]["mp3-128"],
                duration=track["duration"]
            )
        )
    return tracks


def search_albums_by_tag(tag, sort="pop", generator=False):
    """Search albums by tag

    Params:
        tag - any music tag from get_all_tags()
        sort - sorting type, can be "pop" (best-selling) or "date" (new arrivals), default is "pop"
        generator - use yield instead of return list()

    Returns:
        list (default) or generator of Album objects
    """
    def _get_results_page(tag, sort, page):
        html = _http_get("https://bandcamp.com/tag/{}?sort_field={}&page={}".format(tag, sort, page)).text
        parsed_html = BeautifulSoup(html, HTML_PARSER)
        html_album_list = parsed_html.find_all("li", attrs={"class": ["item ", "item end"]})
        if not html_album_list:
            # we've reached the maximum
            return
        albums = []
        for album_element in html_album_list:
            title = album_element.find("div", attrs={"class": "itemtext"}).string
            artist = album_element.find("div", attrs={"class": "itemsubtext"}).string
            url = album_element.a["href"]
            albums.append(Album(title, artist, url))
        return albums

    def _act_as_generator():
        # 10 is the maximum of available search result pages
        for n in range(1, 11):
            page = _get_results_page(tag, sort, page=n)
            if not page:
                continue
            for album in page:
                yield album

    def _act_as_list():
        albums = []
        # 10 is the maximum of available search result pages
        for n in range(1, 11):
            page = _get_results_page(tag, sort, page=n)
            for album in page:
                albums.append(album)
        return albums

    tag = tag.lower().replace(" ", "-").replace("/", "-")
    if generator is True:
        return _act_as_generator()
    else:
        return _act_as_list()


def get_all_tags():
    """Get all Bandcamp tags

    Returns:
        {"tags": [], "locations": []}
    """
    def get_tags_from_cloud(tags_cloud):
        tags = []
        for possible_found_tag in tags_cloud.find_all("a", attrs={"tag"}):
            if isinstance(possible_found_tag.string, str):
                tags.append(possible_found_tag.string.lower().replace(" ", "-").replace("/", "-"))
        return tags
    html = _http_get("https://bandcamp.com/tags").text
    parsed_html = BeautifulSoup(html, HTML_PARSER)
    tags_cloud = parsed_html.find("div", attrs={"class": "tagcloud", "id": "tags_cloud"})
    locations_cloud = parsed_html.find("div", attrs={"class": "tagcloud", "id": "locations_cloud"})
    tags = get_tags_from_cloud(tags_cloud)
    locations = get_tags_from_cloud(locations_cloud)
    return {"tags": tags, "locations": locations}


if __name__ == "__main__":
    print("This library is designed to be imported, not for standalone use.")
    exit(1)
