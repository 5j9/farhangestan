#!/data/project/farhangestan/www/python/venv/bin/python

"""Provide a web interface to search farhangestan.sqlite3 database."""

import sqlite3

from flask import Flask
from flask import g
from flask import request
from flask import redirect, url_for
from flask import render_template
try:
    from flup.server.fcgi import WSGIServer
except ImportError:
    WSGIServer = False


APP = Flask(__name__)

CLEANUP_TALBE = ''.maketrans({
    'ك': 'ک',
    'ڪ': 'ک',
    'ﻙ': 'ک',
    'ﻚ': 'ک',
    'ي': 'ی',
    'ى': 'ی',
    'ے': 'ی',
    'ۍ': 'ی',
    'ې': 'ی',
    'ہ': 'ه',
    'ھ': 'ه',
})


@APP.route('/')
def searchform():
    return redirect(url_for('static', filename='searchform.html'))


def input_cleanup(text):
    """Replace all semi-Persian characters with standard Persian characters.

    Some of the substations are copied from:
    fa.wikipedia: Mediawiki:Gadget-Extra-Editbuttons-persiantools.js

    """
    return text.translate(CLEANUP_TALBE).replace('ە', 'ه\u200c')


@APP.route('/results' if WSGIServer else '/farhangestan/results')
def searchresult():
    get_arg = request.args.get
    daftar = get_arg('daftar', '')
    word = input_cleanup(get_arg('word', ''))
    wordstart = input_cleanup(get_arg('wordstart', ''))
    wordend = input_cleanup(get_arg('wordend', ''))
    hozeh = input_cleanup(get_arg('hozeh', ''))
    daftar = int(daftar) if daftar.isnumeric() else None
    offset = int(get_arg('offset', 0))
    rows = query_db(word, wordstart, wordend, hozeh, daftar, offset)
    return render_template(
        'results.html', wsgiserver=WSGIServer, word=word, wordend=wordend,
        wordstart=wordstart, hozeh=hozeh, daftar=daftar, rows=rows,
    )


def get_db():
    db = getattr(g, 'db', None)
    if db is None:
        db = g.db = sqlite3.connect('farhangestan.sqlite3')
    return db


@APP.teardown_appcontext
def close_connection(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


def query_db(word, wordstart, wordend, hozeh, daftar, offset):
    query = """
        SELECT mosavab, biganeh, hozeh, tarif, daftar
        FROM words
        WHERE
    """
    args = []
    in_where = False
    if word:
        query += '''(
            mosavab LIKE ?
            OR biganeh LIKE ?
            OR tarif LIKE ?
            OR pure_mosavab LIKE ?
        ) '''
        in_where = True
        args += ('%' + word + '%',) * 4
    if wordstart:
        if in_where:
            query += 'AND '
        else:
            in_where = True
        query += '(mosavab LIKE ? OR biganeh LIKE ?) '
        args += (wordstart + '%',) * 2
    if wordend:
        if in_where:
            query += 'AND '
        else:
            in_where = True
        query += '(mosavab LIKE ? OR biganeh LIKE ?) '
        args += ('%' + wordend,) * 2
    if hozeh:
        if in_where:
            query += 'AND '
        else:
            in_where = True
        query += 'hozeh LIKE ? '
        args += ('%' + hozeh + '%',)
    if daftar:
        if in_where:
            query += 'AND '
        # else:
        #     in_where = True
        query += 'daftar LIKE ? '
        args += (daftar,)
    query += 'LIMIT 50 '
    if offset:
        query += 'OFFSET ? '
        args += (offset,)
    return get_db().execute(query, args).fetchall()


if __name__ == '__main__':
    if WSGIServer:
        WSGIServer(APP).run()
    else:
        APP.run(debug=True)
