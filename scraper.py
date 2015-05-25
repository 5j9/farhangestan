"""This module can be used to scrap the persianacademy website
 ("http://www.persianacademy.ir/fa/word/") and create a database of all the
 words found there.

The database will be stored as `farhangestan.db` while scrapping and will be
 renamed to `farhangestan.sqlite3` after it's ready.
"""

import sqlite3
import re
import os

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


def create_sqlite_file(conn):
    """Create the database file."""
    conn.execute('''CREATE TABLE words (
        mosavab TEXT,
        biganeh TEXT,
        hozeh TEXT,
        tarif TEXT,
        daftar INTEGER
    )'''
    )


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

        
headers = {
    'Host': 'www.persianacademy.ir',
    'User-Agent': 'Mozilla/5.0 ('
    'Windows NT 6.3; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.7,fa;q=0.3',
    'Accept-Encoding': 'gzip, deflate',
    'DNT': 1,
    'Referer': 'http://www.persianacademy.ir/fa/word/',
    'Connection': 'keep-alive',
}

conn = sqlite3.connect('farhangestan.db')
url = 'http://www.persianacademy.ir/fa/word/'
session = requests.Session()

for daftar in range(1, 12):
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
    rows = extract_data(soup, daftar)
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
        data['__EVENTVALIDATION'] = soup.find(id="__EVENTVALIDATION")['value']
        data['__VIEWSTATE'] = soup.find(id="__VIEWSTATE")['value']
        soup = BeautifulSoup(session.post(url, data, headers=headers).content)
        rows = extract_data(soup, daftar)
        insert(rows, conn)

    
conn.close()
os.rename('farhangestan.db', 'farhangestan.sqlite3')
print('`farhangestan.sqlite3` is ready.')
