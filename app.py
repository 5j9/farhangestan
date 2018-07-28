#!/data/project/farhangestan/www/python/venv/bin/python

"""Provide a web interface to search farhangestan.sqlite3 database."""

import sqlite3

from flask import Flask
from flask import request
from flask import redirect, url_for
from flask import render_template
try:
    from flup.server.fcgi import WSGIServer
except ImportError:
    WSGIServer = False


app = Flask(__name__)
conn = None

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


@app.route('/')
def searchform():
    return redirect(url_for('static', filename='searchform.html'))


def input_cleanup(text):
    """Replace all semi-Persian characters with standard Persian characters.

    Some of the substations are copied from:
    fa.wikipedia: Mediawiki:Gadget-Extra-Editbuttons-persiantools.js

    """
    return text.translate(CLEANUP_TALBE).replace('ە', 'ه\u200c')


@app.route('/results' if WSGIServer else '/farhangestan/results')
def searchresult():
    get_arg = request.args.get
    daftar = get_arg('daftar', '')
    if daftar.isnumeric():
        daftar_int = int(daftar)
        daftar = str(daftar_int)
    else:
        daftar_int = 0
        daftar = ''
    word = input_cleanup(get_arg('word', ''))
    wordstart = input_cleanup(get_arg('wordstart', ''))
    wordend = input_cleanup(get_arg('wordend', ''))
    hozeh = input_cleanup(get_arg('hozeh', ''))
    offset = int(get_arg('offset', 0))
    rows = query_db(daftar, word, wordstart, wordend, hozeh, offset)
    return render_template(
        'results.html', wsgiserver=WSGIServer, word=word, wordend=wordend,
        wordstart=wordstart, hozeh=hozeh, daftar=daftar_int, rows=rows,
    )


def query_db(*args):
    global conn
    conn = conn or sqlite3.connect(
        'farhangestan.sqlite3',
        check_same_thread=False,  # since we don't have any writing operations
    )
    return conn.execute(*query_and_args(*args)).fetchall()


def query_and_args(daftar, word, wordstart, wordend, hozeh, offset):
    query = """
        SELECT mosavab, biganeh, hozeh, tarif, daftar
        FROM words
    """
    args = []
    if word:
        query += '''WHERE (
            mosavab LIKE ?
            OR biganeh LIKE ?
            OR tarif LIKE ?
            OR pure_mosavab LIKE ?
        ) '''
        in_where = True
        args += ('%' + word + '%',) * 4
    else:
        in_where = False
    if wordstart:
        if in_where:
            query += 'AND '
        else:
            query += 'WHERE '
            in_where = True
        query += '(mosavab LIKE ? OR biganeh LIKE ?) '
        args += (wordstart + '%',) * 2
    if wordend:
        if in_where:
            query += 'AND '
        else:
            query += 'WHERE '
            in_where = True
        query += '(mosavab LIKE ? OR biganeh LIKE ?) '
        args += ('%' + wordend,) * 2
    if hozeh:
        if in_where:
            query += 'AND '
        else:
            query += 'WHERE '
            in_where = True
        query += 'hozeh LIKE ? '
        args += ('%' + hozeh + '%',)
    if daftar:
        if in_where:
            query += 'AND '
        else:
            query += 'WHERE '
        query += 'daftar = ? '
        args += (daftar,)
    query += 'LIMIT 50 '
    if offset:
        query += 'OFFSET ? '
        args += (offset,)
    return query, args


if __name__ == '__main__':
    if WSGIServer:
        WSGIServer(app).run()
    else:
        app.run(debug=True)
