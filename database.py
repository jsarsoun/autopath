import sqlite3
import pandas as pd

DATABASE = 'data.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS csv_data')
    c.execute('DROP TABLE IF EXISTS pdf_files')
    c.execute('''CREATE TABLE csv_data
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  content TEXT)''')
    c.execute('''CREATE TABLE pdf_files
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  filename TEXT)''')
    conn.commit()
    conn.close()

def insert_data(df, file_type):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    if file_type == 'csv':
        content = df.to_json(orient='records')
        cursor.execute("INSERT INTO csv_data (content) VALUES (?)", (content,))
    elif file_type == 'pdf':
        filename = df['filename'].iloc[0]
        cursor.execute("INSERT INTO pdf_files (filename) VALUES (?)", (filename,))
    
    conn.commit()
    conn.close()

def get_all_data():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM csv_data")
    rows = cursor.fetchall()
    conn.close()

    data = []
    for row in rows:
        df = pd.read_json(row[1])
        for record in df.to_dict(orient='records'):
            record['id'] = row[0]
            data.append(record)

    return pd.DataFrame(data)

def get_pdf_files():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pdf_files")
    rows = cursor.fetchall()
    conn.close()

    return [{'id': row[0], 'filename': row[1]} for row in rows]
