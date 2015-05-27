#!/data/project/farhangestan/ve/bin/python

"""A web application that allows searching the farhangestan.sqlite3 database.
"""

import sqlite3
from os import name as os_name
if os_name == 'posix':
    from flup.server.fcgi import WSGIServer

from flask import Flask
from flask import g
from flask import request
from flask import redirect, url_for
from flask import render_template


app = Flask(__name__)

@app.route('/')
def searchform():
    return redirect(url_for('static', filename='searchform.html'))


@app.route('/results')
def searchresult():
    args = request.args
    daftar = args.get('daftar', '')
    query = (
        "SELECT * FROM words WHERE "
        "(mosavab LIKE ? OR "
        "biganeh LIKE ? OR "
        "tarif LIKE ?)"
        " AND "
        "(mosavab LIKE ? OR "
        "biganeh LIKE ? OR "
        "tarif LIKE ?)"
        " AND "
        "(mosavab LIKE ? OR "
        "biganeh LIKE ? OR "
        "tarif LIKE ?)"
        " AND "
        "hozeh LIKE ?"
        " AND "
        "daftar LIKE ?"
        " LIMIT 100;"
    )
    word = args.get('word', '')
    wordstart = args.get('wordstart', '')
    wordend = args.get('wordend', '')
    hozeh = args.get('hozeh', '')
    daftar = int(daftar) if daftar.isnumeric() else ''
    
    rows = query_db(
        query,
        ('%{}%'.format(word),)* 3 + ('{}%'.format(wordstart),)* 3 +
        ('%{}'.format(wordend),)* 3 + ('%{}%'.format(hozeh),) +
        ('%{}%'.format(daftar),),
    )
    
    return render_template('results.html', rows=rows)


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
