#!/usr/bin/env python3

"""This module can be used to scrap the persianacademy website
 ("http://www.persianacademy.ir/fa/word/") and create a database of all the
 words found there.

The database will be stored as `farhangestan.sqlite3`.
"""

import sqlite3
import re

import requests
from bs4 import BeautifulSoup


def extract_data(soup, daftar):
    """Extract data in soup and write it into the connection."""
    rows = []
    table = soup.find(id="MainSection_dgData")
    for tr in table('tr')[1:]:
        tds = tr('td')
        if len(tds) == 4:
            rows.append([td.text for td in tds] + [daftar])
    return rows


def create_sqlite_file():
    """Create the database file. Return connection object."""
    conn = sqlite3.connect('farhangestan.sqlite3')
    conn.execute('''CREATE TABLE words (
        mosavab TEXT,
        biganeh TEXT,
        hozeh TEXT,
        tarif TEXT,
        daftar INTEGER
    )'''
    )
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
                daftar
                )
            VALUES (?, ?, ?, ?, ?)
            """,
            rows
        )


def replace_in_table(conn, old, new):
    for col in ('mosavab', 'biganeh', 'hozeh', 'tarif', 'daftar'):
        sql = """
        UPDATE words
        SET {col} = replace({col}, '{old}', '{new}')
        WHERE {col} LIKE '%{old}%';
        """.format(old=old, new=new, col=col)
        conn.execute(sql)
        conn.commit()

def add_pure_mosavab_column(conn):
    """Create a new column named `pure_mosavab` that has no diacritics.

    Note: This may take a while!
    """
    try:
        sql = "ALTER TABLE words ADD COLUMN pure_mosavab TEXT;"
        conn.execute(sql)
        conn.commit()
    except sqlite3.OperationalError:
        # duplicate column name: pure_mosavab
        pass
    diacritics = "\u0651\u064E\u0650\u064F\u064B\u064D\u064C\u0652"
    sql = (
        """
        SELECT mosavab
        FROM words
        WHERE mosavab LIKE '%""" + """%'
         OR mosavab LIKE '%""".join(diacritics) +
        "%';"
    )
    cur = conn.execute(sql)
    for row in cur.fetchall():
        mosavab = row[0]
        pure_mosavab = mosavab
        for d in diacritics:
            pure_mosavab = pure_mosavab.replace(d, '')
        conn.execute(
            "update or replace words set pure_mosavab = ? where mosavab = ?",
            (pure_mosavab, mosavab),
        )
    conn.commit()

        
if __name__ == '__main__':
    headers = {
        'Host': 'www.persianacademy.ir',
        'User-Agent': 'Mozilla/5.0 ('
        'Windows NT 6.3; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q='
        '0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.7,fa;q=0.3',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': 1,
        'Referer': 'http://www.persianacademy.ir/fa/word/',
        'Connection': 'keep-alive',
    }

    conn = create_sqlite_file()
    url = 'http://www.persianacademy.ir/fa/word/'
    session = requests.Session()

    daftar = 0
    while True:
        daftar += 1
        page = 1
        print(daftar, page)
        soup = BeautifulSoup(session.get(url, headers=headers).content)
        
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

        soup = BeautifulSoup(session.post(url, data, headers=headers).content)
        try:
            rows = extract_data(soup, daftar)
        except TypeError:
            # This `daftar` has no words (is not released yet)
            break
        insert(rows, conn)
        
        
        del data['ctl00$MainSection$btnSearch']
        while True:
            page += 1
            print(daftar, page)
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
                session.post(url, data, headers=headers).content
            )
            rows = extract_data(soup, daftar)
            insert(rows, conn)

    

    replace_in_table(conn, 'ۀ', 'هٔ')
    replace_in_table(conn, '\u200F', '\u200C')
    add_pure_mosavab_column(conn)
    conn.close()
    print('`farhangestan.sqlite3` is ready.')
