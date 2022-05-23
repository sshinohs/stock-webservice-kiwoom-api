import pymysql.cursors
import mysql_auth
import json


def kiwoom_login(login_info):
    conn = pymysql.connect(
        host=login_info['host'],
        port=login_info['port'],
        user=login_info['user'],
        password=login_info['passwd'],
        database=login_info['db'],
        charset=login_info['charset']
    )
    return conn


def load_json(file_name):
    with open(file_name, 'r') as f:
        json_data = json.load(f)
    return json_data


def mysql_query(connect, cursor, query, data):
    cursor.execute(query, data)
    connect.commit()


login_info = mysql_auth.info
conn = kiwoom_login(login_info)
curs = conn.cursor()

files = ['./file/kospi.json', './file/kosdaq.json']

sql = "INSERT INTO items(code, name) VALUES (%s, %s)"

for fn in files:
    json_data = load_json(fn)
    for key, val in json_data.items():
        dat = (key, val)
        curs.execute(sql, dat)
        conn.commit()