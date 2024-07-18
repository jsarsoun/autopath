import os
from flask import Flask, request, render_template, redirect, url_for, flash
import pandas as pd
from database import init_db, insert_data, get_all_data

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'csv'}
app.config['SECRET_KEY'] = 'your_secret_key_here'  # Add this line for flash messages

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

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
                # Parse CSV and insert data into the database
                df = pd.read_csv(filename)
                insert_data(df)
                flash('File uploaded and data stored successfully!', 'success')
            except Exception as e:
                flash(f'Error processing file: {str(e)}', 'error')
            
            return redirect(url_for('upload_file'))
        else:
            flash('Invalid file type. Please upload a CSV file.', 'error')
            return redirect(request.url)
    
    # Get all data from the database
    data = get_all_data()
    return render_template('index.html', data=data)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
