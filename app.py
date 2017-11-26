#!/data/project/farhangestan/www/python/venv/bin/python

"""Provide a web interface to search farhangestan.sqlite3 database."""

import sqlite3
from os import name as os_name

from flask import Flask
from flask import g
from flask import request
from flask import redirect, url_for
from flask import render_template
if os_name == 'posix':
    from flup.server.fcgi import WSGIServer


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
app = Flask(__name__)

@app.route('/')
def searchform():
    return redirect(url_for('static', filename='searchform.html'))


def input_cleanup(text: str):
    """Replace all semi-Persian characters with standard Persian characters.

    Some of the substations are copied from:
    fa.wikipedia: Mediawiki:Gadget-Extra-Editbuttons-persiantools.js

    """
    return text.translate(CLEANUP_TALBE).replace('ە', 'ه\u200c')


@app.route('/results' if os_name == 'posix' else '/farhangestan/results')
def searchresult():
    get_arg = request.args.get
    daftar = get_arg('daftar', '')
    query = (
        "SELECT mosavab, biganeh, hozeh, tarif, daftar FROM words WHERE "
        "(mosavab LIKE ? OR "
        "biganeh LIKE ? OR "
        "tarif LIKE ? OR "
        "pure_mosavab LIKE ?)"
        " AND "
        "(mosavab LIKE ? OR "
        "biganeh LIKE ?)"
        " AND "
        "(mosavab LIKE ? OR "
        "biganeh LIKE ?)"
        " AND "
        "hozeh LIKE ?"
        " AND "
        "daftar LIKE ?"
        " LIMIT 50 OFFSET ?;"
    )
    word = input_cleanup(get_arg('word', ''))
    wordstart = input_cleanup(get_arg('wordstart', ''))
    wordend = input_cleanup(get_arg('wordend', ''))
    hozeh = input_cleanup(get_arg('hozeh', ''))
    daftar = int(daftar) if daftar.isnumeric() else ''
    offset = int(get_arg('offset', 0))
    rows = query_db(
        query,
        ('%{}%'.format(word),) * 4 + ('{}%'.format(wordstart),) * 2 +
        ('%{}'.format(wordend),) * 2 + ('%{}%'.format(hozeh),) +
        ('%{}%'.format(daftar),) + (offset,),
    )
    return render_template(
        'results.html', os_name=os_name, word=word, wordend=wordend,
        wordstart=wordstart, hozeh=hozeh, daftar=daftar, rows=rows,
    )


def connect_to_db():
    """Connects to the specific database."""
    return sqlite3.connect('farhangestan.sqlite3')


def get_db():
    db = getattr(g, 'db', None)
    if db is None:
        db = g.db = connect_to_db()
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


def query_db(query, args):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return rv


if __name__ == '__main__':
    if os_name == 'posix':
        WSGIServer(app).run()
    else:
        app.run(debug=True)
