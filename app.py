import os
from flask import Flask, request, render_template, redirect, url_for
import pandas as pd
from database import init_db, insert_data

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'csv'}

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)
            
            # Parse CSV and insert data into the database
            df = pd.read_csv(filename)
            insert_data(df)
            
            return 'File uploaded and data stored successfully!'
    return render_template('index.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
