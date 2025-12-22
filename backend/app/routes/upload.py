from flask import Blueprint, request, current_app, send_from_directory, url_for
from flask_jwt_extended import jwt_required
from app.utils.responses import success_response, error_response
import os
import uuid
from werkzeug.utils import secure_filename

upload_bp = Blueprint('upload', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'txt', 'webm', 'mp3', 'wav'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_bp.route('/', methods=['POST'])
@jwt_required()
def upload_file():
    if 'file' not in request.files:
        return error_response('No file part', None, 400)
        
    file = request.files['file']
    
    if file.filename == '':
        return error_response('No selected file', None, 400)
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Unique filename to avoid collisions
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        
        # Ensure upload directory exists
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        
        file.save(os.path.join(upload_folder, unique_filename))
        
        # Generate URL
        # Assuming we serve static from /static/uploads
        file_url = f"/static/uploads/{unique_filename}"
        
        return success_response('File uploaded successfully', {'url': file_url}, 201)
        
    return error_response('File type not allowed', None, 400)

@upload_bp.route('/<path:filename>')
def serve_file(filename):
    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
    return send_from_directory(upload_folder, filename)
