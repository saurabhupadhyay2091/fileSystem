# sample_app.py
import os
from flask import Flask, request, flash, send_file, redirect, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from celery import Celery
from zipfile import ZipFile
from io import BytesIO

# Flask app configuration
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:ranktech@localhost:5432/flask_db'  # Update with your PostgreSQL connection details
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['CELERY_BROKER_URL'] = 'amqp://saurabh:saurabh@localhost:5672'  # Update with your RabbitMQ broker URL

# Database setup
db = SQLAlchemy(app)

# Celery setup
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])


# File model
class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100))
    path = db.Column(db.String(200))
    folder_id = db.Column(db.Integer, db.ForeignKey('folder.id'))

    def as_dict(self):
        return {'id': self.id, 'filename': self.filename, 'path': self.path}


# Folder model
class Folder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    parent_id = db.Column(db.Integer, db.ForeignKey('folder.id'))
    files = db.relationship('File', backref='folder', lazy=True)
    subfolders = db.relationship('Folder', backref=db.backref('parent', remote_side=[id]), lazy=True)

    def as_dict(self):
        return {'id': self.id, 'name': self.name, 'parent_id': self.parent_id}


# Celery task to handle file uploads asynchronously
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

            # Process file upload asynchronously
            process_file_upload.apply_async(args=(path, filename))

            flash('File upload initiated successfully.')
            return redirect('/')

    return render_template('upload.html')


# Celery task to handle file downloads asynchronously
@celery.task
def process_file_download(file_path, filename):
    return file_path, filename


@app.route('/download/file/<int:file_id>')
def download_file(file_id):
    file_record = File.query.get(file_id)
    if file_record:
        # Process file download asynchronously
        result = process_file_download.apply_async(args=(file_record.path, file_record.filename))
        return redirect(url_for('download_file_async', task_id=result.id))

    flash('File not found.')
    return redirect('/')


@app.route('/download/file/async/<string:task_id>')
def download_file_async(task_id):
    result = process_file_download.AsyncResult(task_id)
    if result.ready():
        file_path, filename = result.result
        return send_file(file_path, as_attachment=True, attachment_filename=filename)

