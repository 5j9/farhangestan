#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Scrap the Persian Academy website to create a local sqlite3 database.

Web address: "http://www.persianacademy.ir/fa/word/".
Save the sqllite3 database as `farhangestan.sqlite3`.

"""


import sqlite3
import re

import requests
from bs4 import BeautifulSoup


DIACRITICS_TT = str.maketrans(
    '', '', '\u0651\u064E\u0650\u064F\u064B\u064D\u064C\u0652'
)
GENERAL_TT = str.maketrans('\u200F', '\u200C')


def cleanup_tds(tds):
    """Replace some of the known bad characters with better equivalents."""
    for i, d in enumerate(tds):
        tds[i] = (
            d.text.
            replace('ۀ', 'هٔ').
            replace('\u064B\u064B', '\u064B').
            translate(GENERAL_TT).
            strip()
        )
    return tds


def extract_data(soup, daftar):
    """Extract data in soup and write it into the connection."""
    rows = []
    table = soup.find(id='MainSection_dgData')
    for tr in table('tr')[1:]:
        tds = tr('td')
        if len(tds) == 4:
            tds = cleanup_tds(tds)
            mosavab = tds[0]
            pure_mosavab = mosavab.translate(DIACRITICS_TT)
            if pure_mosavab == mosavab:
                rows.append([td for td in tds] + [daftar, None])
            else:
                rows.append([td for td in tds] + [daftar, pure_mosavab])
    return rows


def max_dafter(conn):
    """Return the maximum value of daftar in the existing table."""
    return conn.execute('SELECT max(daftar) FROM words;').fetchone()[0]


def get_conn():
    """Create/connect to the database file. Return the connection object."""
    conn = sqlite3.connect('farhangestan.sqlite3')
    try:
        conn.execute(
            '''
            CREATE TABLE words (
            mosavab TEXT,
            biganeh TEXT,
            hozeh TEXT,
            tarif TEXT,
            daftar INTEGER,
            pure_mosavab TEXT
            )
            '''
        )
    except sqlite3.OperationalError:
        # table words already exists
        pass
    return conn


def insert(rows, conn):
    """Insert the given row into the database."""
    with conn as c:
        c.executemany(
            """
            INSERT INTO words (
                mosavab,
                biganeh,
                hozeh,
                tarif,
                daftar,
                pure_mosavab
                )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            rows
        )


def trim_table_values(chars: str):
    conn = get_conn()
    for col in ('mosavab', 'biganeh', 'hozeh', 'tarif', 'daftar'):
        sql = """
        UPDATE words
        SET {col} = trim({col}, '{chars}');
        """.format(col=col, chars=chars)
        conn.execute(sql)
        conn.commit()


def replace_in_table(conn, old: str, new: str):
    """Replace old with new in columns of the table.

    Only done on ('mosavab', 'biganeh', 'hozeh', 'tarif', 'daftar') fields.

    """
    for col in ('mosavab', 'biganeh', 'hozeh', 'tarif', 'daftar'):
        sql = """
        UPDATE words
        SET {col} = replace({col}, '{old}', '{new}')
        WHERE {col} LIKE '%{old}%';
        """.format(old=old, new=new, col=col)
        conn.execute(sql)
        conn.commit()


def scrap_and_store():
    headers = {
        'Host': 'www.persianacademy.ir',
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:38.0) '
            'Gecko/20100101 Firefox/38.0'
        ),
        'Accept': (
            'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        ),
        'Accept-Language': 'en-US,en;q=0.7,fa;q=0.3',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Referer': 'http://www.persianacademy.ir/fa/word/',
        'Connection': 'keep-alive',
    }

    conn = get_conn()
    daftar = max_dafter(conn)

    url = 'http://www.persianacademy.ir/fa/word/'
    session = requests.Session()

    while True:
        daftar += 1
        page = 1
        print('Book:', daftar, 'Page:', page)
        soup = BeautifulSoup(
            session.get(url, headers=headers).text,
            "html5lib",
        )

        data = {
            '__VIEWSTATE': soup.find(id="__VIEWSTATE")['value'],
            '__EVENTVALIDATION': soup.find(id="__EVENTVALIDATION")['value'],
            'ctl00$MainSection$hidAll': '',
            'ctl00$MainSection$hidWhichButton': '',
            'ctl00$MainSection$txtFaWord': '',
            'ctl00$MainSection$txtVersion': daftar,
            'ctl00$MainSection$txtRegion': '',
            'ctl00$MainSection$txtEnWord': '',
            'ctl00$MainSection$txtDesc': '',
            'ctl00$MainSection$btnSearch': 'جست‌و‌جو',
        }

        soup = BeautifulSoup(
            session.post(url, data, headers=headers).text,
            "html5lib",
        )
        try:
            rows = extract_data(soup, daftar)
        except TypeError:
            print('Book {} has no words.'.format(daftar))
            break
        insert(rows, conn)

        del data['ctl00$MainSection$btnSearch']
        while True:
            page += 1
            print('Book:', daftar, 'Page:', page)
            data['__EVENTARGUMENT'] = ''
            pagelink = soup.find(colspan=4).find(text=page)
            if pagelink:
                data['__EVENTTARGET'] = re.search(
                    r"\(\'(.*?)\'", str(pagelink.parent)
                ).group(1)
            elif soup.find(colspan=4).text.endswith('...'):
                data['__EVENTTARGET'] = re.search(
                    r"\(\'(.*?)\'", str(soup.find(colspan=4)('a')[-1])
                ).group(1)
            else:
                break
            data['__EVENTVALIDATION'] = soup.find(
                id="__EVENTVALIDATION"
            )['value']
            data['__VIEWSTATE'] = soup.find(id="__VIEWSTATE")['value']
            soup = BeautifulSoup(
                session.post(url, data, headers=headers).text,
                "html5lib",
            )
            rows = extract_data(soup, daftar)
            insert(rows, conn)

    conn.close()
    print('farhangestan.sqlite3 is ready!')


if __name__ == '__main__':
    scrap_and_store()
    # trim_table_values(' ')
