import os
from flask import Flask, request, render_template, redirect, url_for, flash
import pandas as pd
from PyPDF2 import PdfReader
from database import init_db, insert_data, get_all_data

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'csv', 'pdf'}
app.config['SECRET_KEY'] = 'your_secret_key_here'

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def process_pdf(filename):
    with open(filename, 'rb') as file:
        pdf = PdfReader(file)
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return pd.DataFrame({'content': [text]})

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)
            
            try:
                if filename.lower().endswith('.csv'):
                    df = pd.read_csv(filename)
                elif filename.lower().endswith('.pdf'):
                    df = process_pdf(filename)
                insert_data(df)
                flash('File uploaded and data stored successfully!', 'success')
            except Exception as e:
                flash(f'Error processing file: {str(e)}', 'error')
            
            return redirect(url_for('upload_file'))
        else:
            flash('Invalid file type. Please upload a CSV or PDF file.', 'error')
            return redirect(request.url)
    
    # Get all data from the database
    df = get_all_data()
    return render_template('index.html', data=df.to_dict(orient='records'), columns=df.columns)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
