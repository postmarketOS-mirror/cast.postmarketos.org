import collections
import subprocess

import logo
import markdown
import os
import re
import yaml

from atom import AtomFeed

from datetime import datetime
from flask import Flask, render_template, url_for, Response, request, \
    send_file, jsonify

app = Flask(__name__)

PAGE_CONTENT_DIR = 'content/page'
CAST_CONTENT_DIR = 'content/cast'

REGEX_SPLIT_FRONTMATTER = re.compile(r'^---$', re.MULTILINE)


def parse_episode(post):
    with open(os.path.join(CAST_CONTENT_DIR, post),
              encoding="utf-8") as handle:
        raw = handle.read()
    frontmatter, content = REGEX_SPLIT_FRONTMATTER.split(raw, 2)

    data = yaml.load(frontmatter)

    data['html'] = markdown.markdown(content, extensions=[
        'markdown.extensions.extra',
    ])
    data['url'] = url_for('episode', episode=post.replace('.md', ''),
                          _external=True)
    data['chapters_url'] = url_for('chapters', episode=post.replace('.md', ''),
                                   _external=True)
    data['opus'] = url_for('static',
                           filename='audio/' + post.replace('.md', '.opus'),
                           _external=True)
    data['mpeg'] = url_for('static',
                           filename='audio/' + post.replace('.md', '.mp3'),
                           _external=True)
    raw = data['timestamps']
    data['timestamps'] = []
    for mark in raw:
        time, label = mark.split(' ')
        minutes, seconds = time.split(':')
        seconds = float(seconds) + (60 * int(minutes))
        data['timestamps'].append([time, label, seconds])
    return data


def get_episodes():
    for filename in sorted(os.listdir(CAST_CONTENT_DIR), reverse=True):
        parsed = parse_episode(filename)
        yield parsed


@app.route('/')
def home():
    with open(os.path.join(PAGE_CONTENT_DIR, 'index.md'),
              encoding="utf-8") as handle:
        raw = handle.read()
    frontmatter, content = REGEX_SPLIT_FRONTMATTER.split(raw, 2)
    data = yaml.load(frontmatter)
    data['html'] = markdown.markdown(content, extensions=[
        'markdown.extensions.extra',
        'markdown.extensions.codehilite',
        'markdown.extensions.toc'
    ], extension_configs={"markdown.extensions.toc": {"anchorlink": True}})

    data['episodes'] = list(get_episodes())

    return render_template('index.html', **data)


@app.route('/episode/2020-12/')
def first_episode_redirect():
    # This episode used to have only the date as slug.
    return render_template("redirect.html", url="/episode/01-History/")


@app.route('/episode/<episode>/')
def episode(episode):
    data = parse_episode(episode + '.md')
    return render_template('episode.html', **data)


@app.route('/episode/<episode>/chapters.json')
def chapters(episode):
    data = parse_episode(episode + '.md')
    result = []
    for mark in data['timestamps']:
        result.append({
            "startTime": mark[2],
            "title": mark[1]
        })
    return jsonify(version="1.0.0", chapters=result)


@app.route('/robots.txt')
def robots_txt():
    return send_file('static/robots.txt')


@app.route('/.well-known/dnt-policy.txt')
def dnt_policy():
    return send_file('static/dnt-policy.txt')


@app.route('/logo.svg')
def logo_svg():
    return Response(response=logo.create(phone=False),
                    mimetype="image/svg+xml")


def static_file_size(url):
    host, filename = url.split('static/')
    path = "static/" + filename
    return os.path.getsize(path)


@app.route('/feed-legacy.rss', defaults={"fmt": "mpeg"}, endpoint='legacyatom')
@app.route('/feed.rss', defaults={"fmt": "opus"})
def atom(fmt):
    feed = AtomFeed(author='postmarketOS',
                    feed_url=request.url,
                    icon=url_for('logo_svg', _external=True),
                    title='postmarketOS Podcast',
                    url=url_for('home', _external=True),
                    cover_url=url_for('static',
                                      filename='img/cover.jpg',
                                      _external=True),
                    summary="For your postmarketOS podcast episodes")

    for episode in get_episodes():
        guid = None
        if 'guid' in episode:
            guid = episode['guid']

        feed.add(content=episode['html'],
                 content_type='html',
                 title=episode['title'],
                 url=episode['url'],
                 chapters=episode['chapters_url'],
                 # midnight
                 updated=datetime.combine(episode['date'],
                                          datetime.min.time()), files=[
                (f'audio/{fmt}', episode[fmt],
                 static_file_size(episode[fmt]))
            ], guid=guid)
    return feed.get_response()


@app.route("/static/audio/<file>.mp3")
def generate_mp3(file):
    static_path = f'static/audio/{file}.mp3'
    opus = f'static/audio/{file}.opus'
    if not os.path.isfile(static_path):
        subprocess.run(['ffmpeg', '-i', opus, '-b:a', '320k', static_path])
    return send_file(static_path, mimetype='audio/mpeg')


@app.route('/<page>.html')
def static_page(page):
    with open(os.path.join(PAGE_CONTENT_DIR, page + '.md'),
              encoding="utf-8") as handle:
        raw = handle.read()
    frontmatter, content = REGEX_SPLIT_FRONTMATTER.split(raw, 2)
    data = yaml.load(frontmatter)
    data['html'] = markdown.markdown(content, extensions=[
        'markdown.extensions.extra',
        'markdown.extensions.codehilite',
        'markdown.extensions.toc'
    ], extension_configs={"markdown.extensions.toc": {"anchorlink": True}})
    return render_template('page.html', **data)
