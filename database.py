import sqlite3
import pandas as pd

DATABASE = 'data.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS csv_data')
    c.execute('''CREATE TABLE csv_data
                 (id INTEGER PRIMARY KEY AUTOINCREMENT)''')
    conn.commit()
    conn.close()

def insert_data(df):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Add columns to the table based on DataFrame columns
    for column in df.columns:
        cursor.execute(f"ALTER TABLE csv_data ADD COLUMN '{column}' TEXT")
    
    # Insert data
    for _, row in df.iterrows():
        columns = ', '.join(f"'{col}'" for col in df.columns)
        placeholders = ', '.join('?' for _ in df.columns)
        query = f"INSERT INTO csv_data ({columns}) VALUES ({placeholders})"
        cursor.execute(query, tuple(row))
    
    conn.commit()
    conn.close()

def get_all_data():
    conn = sqlite3.connect(DATABASE)
    df = pd.read_sql_query("SELECT * FROM csv_data", conn)
    conn.close()
    return df
