import os
import shutil
from flask import Flask, request, flash, send_file, redirect, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from zipfile import ZipFile
from io import BytesIO
from celery import Celery
from models.file import File
from models.folder import Folder

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://****:***@localhost:5432/filesystem_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['CELERY_BROKER_URL'] = 'amqp://***:***@localhost:5672//'


db = SQLAlchemy(app)

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])



@celery.task
def process_file_upload(file_path, filename):
    # Save file metadata in the database
    file_record = File(filename=filename, path=file_path)
    db.session.add(file_record)
    db.session.commit()


@app.route('/')
def home():
    return 'Welcome to the File System!'


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = file.filename
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(path)
            process_file_upload.apply_async(args=(path, filename))

            flash('File upload initiated successfully.')
            return redirect('/')

    return render_template('upload.html')


@celery.task
def process_file_download(file_path, filename, is_folder):
    if is_folder:
        # Create a zip file for the folder and return its path
        zip_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{filename}.zip')
        with ZipFile(zip_path, 'w') as zip_file:
            for root, dirs, files in os.walk(file_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    zip_file.write(file_path, os.path.relpath(file_path, file_path))
        return zip_path
    else:
        # Return the file path for individual files
        return file_path


@app.route('/download/file/<int:file_id>')
def download_file(file_id):
    file_record = File.query.get(file_id)
    if file_record:
        # Process file download asynchronously
        result = process_file_download.apply_async(args=(file_record.path, file_record.filename, False))
        return redirect(url_for('download_file_async', task_id=result.id))

    flash('File not found.')
    return redirect('/')


@app.route('/download/folder/<int:folder_id>')
def download_folder(folder_id):
    folder_record = Folder.query.get(folder_id)
    if folder_record:
        # Process folder download asynchronously
        result = process_file_download.apply_async(args=(folder_record.path, folder_record.name, True))
        return redirect(url_for('download_file_async', task_id=result.id))

    flash('Folder not found.')
    return redirect('/')


@app.route('/download/file/async/<string:task_id>')
def download_file_async(task_id):
    result = process_file_download.AsyncResult(task_id)
    if result.ready():
        file_path = result.result
        return send_file(file_path, as_attachment=True)

    flash('File or folder is not ready for download yet.')
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
