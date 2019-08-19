import sqlite3
import datetime

DB = "userdb.sqlite3"
DAYS_TO_EXPIRE = 7
MESSAGE = """Hi, I'm a bot, and I'm soon to be open source!"""


def now_date():
    return str(datetime.datetime.now())

def _create_table_1():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    query = """CREATE TABLE users (
        id text PRIMARY KEY,
        username text,
        subreddits text,
        date_updated text
    )"""
    c.execute(query)
    conn.commit()
    conn.close()

def _create_table_2():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    query = """CREATE TABLE subreddits (
        id text PRIMARY KEY,
        name text
    )"""
    c.execute(query)
    conn.commit()
    conn.close()

def jaccard_dist(s1, s2):
    s1 = set(s1.keys())
    s2 = set(s2.keys())
    return len(s1 & s2) / len(s1 | s2)

def overlap_dist(s1, s2):
    s1 = set(s1.keys())
    s2 = set(s2.keys())
    return len(s1 & s2) / min(len(s1), len(s2))

def dice_dist(s1, s2):
    s1 = set(s1.keys())
    s2 = set(s2.keys())
    return (2*len(s1 & s2)) / (len(s1) + len(s2))

def union(s1, s2):
    return set(s1.keys()) & set(s2.keys())

def date_from_str(s):
    return datetime.datetime.strptime(s, '%Y-%m-%d %H:%M:%S.%f')

def subreddit_from_id(id_, r):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    query = """SELECT name FROM subreddits where id = ?"""
    cursor.execute(query, (id_,))
    data = cursor.fetchone()
    if data is None:
        name = list(r.info([id_]))[0].display_name
        query = """INSERT INTO subreddits (id, name) VALUES (?, ?)"""
        cursor.execute(query, (id_, name))
    else:
        name =  data[0]
    conn.commit()
    conn.close()
    return name

def table_str(headings, body):
    s = ""
    s += "|".join(headings) + "\n"
    s += "|".join(":--" for col in headings) + "\n"
    for row in body:
        s += "|".join(row) + "\n"
    return s

def expired_date(dt):
    now = datetime.datetime.now()
    return now - dt > datetime.timedelta(days=DAYS_TO_EXPIRE)
    