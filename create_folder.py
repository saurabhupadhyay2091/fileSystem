from flask import Flask, request, jsonify
import os
import shutil
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename


UPLOAD_FOLDER = 'uploads'

app = Flask(__name__)

@app.route('/createFolder', methods=['POST'])
def create_folder():
    data = request.get_json()
    folder_path = data.get('path')

    if not folder_path:
        return jsonify({'message': 'Path is required'}), 400

    try:
        os.makedirs(folder_path)
    except OSError as e:
        return jsonify({'message': str(e)}), 500

    return jsonify({'message': 'Folder created successfully'}), 201



# Route for file upload
@app.route('/upload', methods=['POST'])
def upload_file():
    files = request.files.getlist('files[]')
    target_folder = request.form.get('folder', '')

    uploaded_files = []
    for file in files:
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, target_folder, filename)
            try:
                file.save(file_path)
            except:
                print("please specify accessible file path")
            uploaded_files.append(filename)

    return jsonify({'uploaded_files': uploaded_files})

if __name__ == '__main__':
    # Create the upload directory if it doesn't exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    app.run()
