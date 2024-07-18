import sqlite3
import pandas as pd

DATABASE = 'data.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS file_data')
    c.execute('''CREATE TABLE file_data
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  file_type TEXT,
                  content TEXT)''')
    conn.commit()
    conn.close()

def insert_data(df):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    if 'content' in df.columns:
        # PDF data
        file_type = 'pdf'
        content = df['content'].iloc[0]
        cursor.execute("INSERT INTO file_data (file_type, content) VALUES (?, ?)", (file_type, content))
    else:
        # CSV data
        file_type = 'csv'
        content = df.to_json(orient='records')
        cursor.execute("INSERT INTO file_data (file_type, content) VALUES (?, ?)", (file_type, content))
    
    conn.commit()
    conn.close()

def get_all_data():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM file_data")
    rows = cursor.fetchall()
    conn.close()

    data = []
    for row in rows:
        if row[1] == 'csv':
            df = pd.read_json(row[2])
            for record in df.to_dict(orient='records'):
                record['id'] = row[0]
                record['file_type'] = 'csv'
                data.append(record)
        else:
            data.append({'id': row[0], 'file_type': 'pdf', 'content': row[2]})

    return pd.DataFrame(data)
