import sqlite3

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

