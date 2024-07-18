import sqlite3
import pandas as pd

DATABASE = 'data.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS csv_data
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  data TEXT)''')
    conn.commit()
    conn.close()

def insert_data(df):
    conn = sqlite3.connect(DATABASE)
    for _, row in df.iterrows():
        data = ','.join(str(value) for value in row)
        conn.execute('INSERT INTO csv_data (data) VALUES (?)', (data,))
    conn.commit()
    conn.close()

def get_all_data():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT * FROM csv_data')
    data = c.fetchall()
    conn.close()
    return data
