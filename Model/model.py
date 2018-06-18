import sqlite3
import time, os

filename = "scrapper_db"
db = None
try:
    #there is need to create a table that will be storing the regex for the various positive scans
    #the table will also have the effects of the various scripts
    #there will therefore alsobe a separate table for storing the scripts extracted from a table, yet to be classified as malicious
    #create/connect to the database
    def connect():
        create = not os.path.exists(filename)
        db = sqlite3.connect(filename)
        if create:
            cursor = db.cursor()

            cursor.execute("CREATE TABLE url_scan ("
                           "scan_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL, "
                           "scan_date TEXT NOT NULL, "
                           "url TEXT NOT NULL,"
                           "last_modified DATETIME NOT NULL )")

            cursor.execute("CREATE TABLE js_string ("
                           "string_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,"
                           "string TEXT NOT NULL,"
                           "regex TEXT ,"
                           "effect_of_js TEXT NOT NULL)")

            cursor.execute("CREATE TABLE scan_report ("
                           "report_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL, "
                           "url TEXT NOT NULL, "
                           "XSS_result TEXT NOT NULL ,"
                           "scan_date DATETIME NOT NULL)")

            cursor.execute("CREATE TABLE positive_scan ("
                           "positive_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL, "
                           "scan_id INTEGER NOT NULL,"
                           "url TEXT NOT NULL,"
                           "string TEXT NOT NULL,"
                           "other_js_string TEXT NOT NULL,"
                           "effect_of_js TEXT NOT NULL,"
                           "remedy TEXT NOT NULL)")
            db.commit()
        return db

    def insert_scan(url, scan_date, last_modified):
        connect()
        db = sqlite3.connect(filename)
        cursor = db.cursor()
        cursor.execute("INSERT INTO url_scan "
                       "(url, scan_date, last_modified)"
                       "VALUES (?, ?, ?)", (url, scan_date, last_modified))
        db.commit()

    def insert_js_string(string, regex, effect_of_js):
        connect()
        db = sqlite3.connect(filename)
        cursor = db.cursor()
        cursor.execute("INSERT INTO js_string "
                       "(string, regex, effect_of_js)"
                       "VALUES (?, ?, ?)", (string, regex, effect_of_js))
        db.commit()

    def insert_scan_report(url, xss_result, scan_date):
        connect()
        db = sqlite3.connect(filename)
        cursor = db.cursor()
        cursor.execute("INSERT INTO scan_report "
                       "(url, xss_result, scan_date)"
                       "VALUES (?, ?, ?)", (url, xss_result, scan_date))
        db.commit()

    def insert_positive_scan(scan_id, url, string, other_js, effect_of_js, remedy):
        connect()
        db = sqlite3.connect(filename)
        cursor = db.cursor()
        cursor.execute("INSERT INTO positive_scan "
                       "(scan_id, url, string, other_js, effect_of_js, remedy)"
                       "VALUES (?, ?, ?, ?, ?, ?)", (scan_id, url, string, other_js, effect_of_js, remedy))
        db.commit()

    def get_js_string(regex):
        connect()
        db = sqlite3.connect(filename)
        cursor = db.cursor()
        cursor.execute("SELECT string FROM js_string WHERE regex = ?", (regex,))
        fields = cursor.fetchone()
        return fields[0] if fields is not None else None

    def get_effect_of_js(regex):
        connect()
        db = sqlite3.connect(filename)
        cursor = db.cursor()
        cursor.execute("SELECT effect_of_js FROM js_string WHERE regex = ?", (regex,))
        fields = cursor.fetchone()
        return fields[0] if fields is not None else None

    def get_url(url):
        connect()
        db = sqlite3.connect(filename)
        cursor = db.cursor()
        cursor.execute("SELECT scan_id FROM url_scan WHERE url = ?", (url,))
        fields = cursor.fetchone()
        return 1 if fields is not None else None

    def get_scan_date(url):
        connect()
        db = sqlite3.connect(filename)
        cursor = db.cursor()
        cursor.execute("SELECT scan_date FROM url_scan WHERE url = ?", (url,))
        fields = cursor.fetchone()
        return fields[0] if fields is not None else None

    def get_report(url):
        connect()
        db = sqlite3.connect(filename)
        cursor = db.cursor()
        cursor.execute("SELECT * FROM scan_report WHERE url = ?", (url,))
        fields = cursor.fetchone()
        return fields[0] if fields is not None else None

    def get_payloads():
        connect()
        db = sqlite3.connect(filename)
        cursor = db.cursor()
        cursor.execute("")
        

finally:
    if db is not None:
        db.close()
