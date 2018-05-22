import sqlite3
import time

filename = "scrapper_db"

#create/connect to the database
def connect(filename):
    create = not os.path.exists(filename)
    db = sqlite3.connect(fileame)
    if create:
        cursor = db.cursor()
        cursor.execute("CREATE TABLE url_scan ("
                       "scan_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL, "
                       "url TEXT NOT NULL,"
                       "last_modified DATETIME NOT NULL )")
        cursor.execute("CREATE TABLE js_string ("
                       "string_id INTEGER PRIMARY KEY AUTOINCREMNET UNIQUE NOT NULL,"
                       "string TEXT NOT NULL,"
                       "regex TEXT ,"
                       "effect_of_js TEXT NOT NULL)")
        cursor.execute("CREATE TABLE scan_report ("
                       "report_id INTEGER PRIMARY KEY NOT NULL AUTOINCREMENT,"
                       "url TEXT NOT NULL ,"
                       "XSS_result TEXT NOT NULL ,"
                       "scan_date DATETIME NOT NULL)")
        cursor.execute("CREATE TABLE positive_scan ("
                       "positive_id INTEGER PRIMARY KEY NOT NULL AUTOINCREMENT,"
                       "scan_id INTEGER NOT NULL,"
                       "url TEXT NOT NULL,"
                       "string TEXT NOT NULL,"
                       "other_js_string TEXT NOT NULL,"
                       "effect_of_js TEXT NOT NULL,"
                       "remedy TEXT NOT NULL)")
        db.commit()
    return db

def insert_scan(url, last_modified=time.time()):
    cursor = db.connect()
    cursor.execute("INSERT INTO url_scan "
                   "(url, last_modified)"
                   "VALUES (?, ?)", (url, last_modified))
    db.commit()

def insert_js_string(string, regex, effect of js):
    cursor = db.connect()
    cursor.execute("INSERT INTO js_string "
                   "(string, regex, effect_of_js)"
                   "VALUES (?, ?, ?)", (string, regex, effect_of_js))
    db.commit()

def insert_scan_report(url, xss_result, scan_date):
    cursor = db.connect()
    cursor.execute("INSERT INTO scan_report "
                   "(url, xss_result, scan_date)"
                   "VALUES (?, ?, ?)", (url, xss_result, scan_date))
    db.commit()

def insert_positive_scan(scan_id, url, string, other_js, effect_of_js, remedy):
    cursor = db.connect()
    cursor.execute("INSERT INTO positive_scan "
                   "(scan_id, url, string, other_js, effect_of_js, remedy)"
                   "VALUES (?, ?, ?, ?, ?, ?)", (scan_id, url, string, other_js, effect_of_js, remedy))
    db.commit()

def get_url():
    cursor = 

def get_report():
    pass
