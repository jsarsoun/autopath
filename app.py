import os
from flask import Flask, request, render_template, redirect, url_for, flash, send_file
import pandas as pd
from database import init_db, insert_data, get_all_data, get_pdf_files, insert_team_points, get_team_points, get_latest_team_points

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'csv', 'pdf', 'xlsx'}
app.config['SECRET_KEY'] = 'your_secret_key_here'

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files or 'file_type' not in request.form:
            flash('No file part or file type not selected', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        file_type = request.form['file_type']
        
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)
        
        if file_type not in app.config['ALLOWED_EXTENSIONS']:
            flash('Invalid file type selected', 'error')
            return redirect(request.url)
        
        if file and file.filename.lower().endswith(f'.{file_type}'):
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)
            
            try:
                if file_type == 'csv':
                    df = pd.read_csv(filename)
                    insert_data(df, file_type)
                elif file_type == 'pdf':
                    insert_data(pd.DataFrame({'filename': [file.filename]}), file_type)
                flash('File uploaded and stored successfully!', 'success')
            except Exception as e:
                flash(f'Error processing file: {str(e)}', 'error')
            
            return redirect(url_for('upload_file'))
        else:
            flash(f'Invalid file type. Please upload a {file_type.upper()} file.', 'error')
            return redirect(request.url)
    
    return render_template('upload.html')

@app.route('/view_csv')
def view_csv():
    csv_data = get_all_data()
    return render_template('view_csv.html', csv_data=csv_data.to_dict(orient='records'), csv_columns=csv_data.columns)

@app.route('/view_pdf')
def view_pdf():
    pdf_files = get_pdf_files()
    return render_template('view_pdf.html', pdf_files=pdf_files)

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)

@app.route('/upload_team_points', methods=['POST'])
def upload_team_points():
    if 'file' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('upload_file'))
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('upload_file'))
    
    if file and file.filename.lower().endswith(('.csv', '.xlsx')):
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)
        
        try:
            if file.filename.lower().endswith('.csv'):
                df = pd.read_csv(filename)
            else:
                df = pd.read_excel(filename)
            
            if 'Team Number' in df.columns and 'Points' in df.columns:
                df = df.rename(columns={'Team Number': 'team', 'Points': 'points'})
                insert_team_points(df)
                flash('Team points uploaded and stored successfully!', 'success')
            else:
                flash('Invalid file format. Please ensure the file has "Team Number" and "Points" columns.', 'error')
        except Exception as e:
            flash(f'Error processing file: {str(e)}', 'error')
        
        return redirect(url_for('upload_file'))
    else:
        flash('Invalid file type. Please upload a CSV or Excel file.', 'error')
        return redirect(url_for('upload_file'))

@app.route('/view_team_points')
def view_team_points():
    all_team_points = get_team_points()
    latest_team_points = get_latest_team_points()
    return render_template('view_team_points.html', all_team_points=all_team_points, latest_team_points=latest_team_points)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
