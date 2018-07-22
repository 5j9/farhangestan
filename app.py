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

QUERY = """
    SELECT mosavab, biganeh, hozeh, tarif, daftar
    FROM words
    WHERE (
        mosavab LIKE ?
        OR biganeh LIKE ?
        OR tarif LIKE ?
        OR pure_mosavab LIKE ?
    ) AND (
        mosavab LIKE ?
        OR biganeh LIKE ?
    ) AND (
        mosavab LIKE ? OR
        biganeh LIKE ?
    ) AND hozeh LIKE ? AND daftar LIKE ?
    LIMIT 50 OFFSET ?;
"""


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
    rows = query_db((
        ('%' + word + '%',) * 4
        + (wordstart + '%',) * 2
        + ('%' + wordend,) * 2
        + ('%' + hozeh + '%',)
        + (daftar,)
        + (offset,)
    ))
    return render_template(
        'results.html', wsgiserver=WSGIServer, word=word, wordend=wordend,
        wordstart=wordstart, hozeh=hozeh, daftar=daftar_int, rows=rows,
    )


def query_db(args):
    global conn
    conn = conn or sqlite3.connect(
        'farhangestan.sqlite3',
        check_same_thread=False,  # since we don't have any writing operations
    )
    return conn.execute(QUERY, args).fetchall()


if __name__ == '__main__':
    if WSGIServer:
        WSGIServer(app).run()
    else:
        app.run(debug=True)
