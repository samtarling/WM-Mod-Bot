import sqlite3


def drop():
    con = sqlite3.connect('config.db')
    cur = con.cursor()
    cur.execute('DROP TABLE config')
    con.commit()
    con.close()


def setup():
    con = sqlite3.connect('config.db')
    cur = con.cursor()
    cur.execute('''CREATE TABLE config (key text UNIQUE, value text)''')
    con.commit()
    con.close()


def read(guild: int, key: str):
    con = sqlite3.connect('config.db')
    cur = con.cursor()
    cur.execute(
        "SELECT * FROM config WHERE key=:key",
        {
            "key": str(guild) + '_' + key

        }
    )
    print(cur.fetchall())


def set(guild: int, key: str, value: str):
    con = sqlite3.connect('config.db')
    cur = con.cursor()
    cur.execute(
        "INSERT INTO config (key, value) VALUES (:key, :value) ON CONFLICT(key) DO UPDATE SET value=:value",
        {
            "key": str(guild) + '_' + key,
            "value": value

        }
    )
    con.commit()
    con.close()