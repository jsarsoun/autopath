import sqlite3
import pandas as pd

DATABASE = 'data.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS csv_data')
    c.execute('DROP TABLE IF EXISTS pdf_files')
    c.execute('DROP TABLE IF EXISTS team_points')
    c.execute('''CREATE TABLE csv_data
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  content TEXT)''')
    c.execute('''CREATE TABLE pdf_files
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  filename TEXT)''')
    c.execute('''CREATE TABLE team_points
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  team TEXT,
                  points INTEGER,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
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

def insert_team_points(df):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Remove existing records for the teams being inserted
    teams = tuple(df['team'].unique())
    cursor.execute(f"DELETE FROM team_points WHERE team IN ({','.join(['?']*len(teams))})", teams)
    
    # Insert new records
    for _, row in df.iterrows():
        cursor.execute("INSERT INTO team_points (team, points) VALUES (?, ?)", (row['team'], row['points']))
    
    conn.commit()
    conn.close()

def get_team_points():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM team_points ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()

    return [{'id': row[0], 'team': row[1], 'points': row[2], 'timestamp': row[3]} for row in rows]

def get_latest_team_points():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t1.*
        FROM team_points t1
        INNER JOIN (
            SELECT team, MAX(timestamp) as max_timestamp
            FROM team_points
            GROUP BY team
        ) t2 ON t1.team = t2.team AND t1.timestamp = t2.max_timestamp
        ORDER BY t1.points DESC
    """)
    rows = cursor.fetchall()
    conn.close()

    return [{'id': row[0], 'team': row[1], 'points': row[2], 'timestamp': row[3]} for row in rows]
