from flask import Flask, render_template, request, send_from_directory, jsonify, redirect, url_for, session
import os
import uuid
from config import Config
from models import db, FileRecord  # Import from models.py
from services.ai_service import generate_yaml_from_topic
from flask import send_file, abort
import io
import base64
from services.document_service import (
    create_pptx_from_yaml,
    create_docx_from_yaml,
    create_pdf_from_yaml,
    create_html_from_yaml
)
from services.preview_service import generate_preview_images
import yaml

app = Flask(__name__)
app.config.from_object(Config)

# Set a 16-character hex secret key for sessions
app.secret_key = 'a1b2c3d4e5f6a7b8'  # Replace this with your own secure 16-char hex string

# Initialize DB and create tables
db.init_app(app)
with app.app_context():
    db.create_all()

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    if Config.ATOM_AUTHENTICATION:
        email = session['email']
        token = session['token']

        print(session)

        return render_template('index.html', email=email, token=token)
    else:
        return render_template('atom_authentication.html')

@app.route('/atom_auth')
def atom():
    global atom_authentication
    Config.ATOM_AUTHENTICATION = True
    token = request.args.get('token')
    email = request.args.get('email')

    session['token'] = token
    session['email'] = email

    return redirect(url_for('index'))    

@app.route('/generate', methods=['POST'])
def generate():

    email = session['email']
    token = session['token']

    topic = request.form.get('topic')
    file_type = request.form.get('file_type')
    html_presentation_type = request.form.get('html_presentation_type', 'minimalist')
    include_images = request.form.get('include_images', 'true').lower() == 'true'
    
    if not topic or not file_type:
        return jsonify({"success": False, "error": "Missing topic or file type"})
    
    if file_type == 'html' and html_presentation_type not in ['minimalist', 'modern', 'professional', 'corporate', 'executive']:
        html_presentation_type = 'minimalist'
    
    file_id = str(uuid.uuid4())
    file_name = f"{topic.replace(' ', '_')}_{file_id}"
    
    yaml_content = generate_yaml_from_topic(topic, include_images=include_images)
    yaml_content_preview = None

    try:
        preview_data = yaml.safe_load(yaml_content)
        yaml_content_preview = preview_data
    except Exception as e:
        return jsonify({"success": False, "error": f"YAML parsing error: {str(e)}"})
    
    preview_images = {}
    if file_type == 'html':
        preview_images = generate_preview_images(yaml_content, topic, app.config['UPLOAD_FOLDER'], email)
    
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
    result = {"success": False, "error": "Invalid file type"}

    if file_type == "pptx":
        full_path = f"{output_path}.pptx"
        result = create_pptx_from_yaml(yaml_content, full_path, topic, email)
        if result["success"]:
            result["file_url"] = f"/download/{file_name}.pptx"
            result["preview"] = yaml_content_preview

    elif file_type == "docx":
        full_path = f"{output_path}.docx"
        result = create_docx_from_yaml(yaml_content, full_path, email)
        if result["success"]:
            result["file_url"] = f"/download/{file_name}.docx"
            result["preview"] = yaml_content_preview

    elif file_type == "pdf":
        full_path = f"{output_path}.pdf"
        result = create_pdf_from_yaml(yaml_content, full_path, email)
        if result["success"]:
            result["file_url"] = f"/download/{file_name}.pdf"
            result["preview"] = yaml_content_preview

    elif file_type == "html":
        full_path = f"{output_path}.html"
        result = create_html_from_yaml(yaml_content, full_path, topic, email, html_presentation_type=html_presentation_type)
        if result["success"]:
            result["file_url"] = f"/download/{file_name}.html"
            result["preview"] = yaml_content_preview
            result["preview_images"] = preview_images

    return jsonify(result)

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/db_download/<int:file_id>')
def db_download_file(file_id):
    file_record = FileRecord.query.get(file_id)
    if not file_record:
        abort(404)

    # Decode base64 content
    decoded_bytes = base64.b64decode(file_record.file_data)

    # Define filename
    filename = f"{file_record.topic.replace(' ', '_')}.{file_record.file_type}"

    # Send as downloadable file
    return send_file(
        io.BytesIO(decoded_bytes),
        as_attachment=True,
        download_name=filename,
        mimetype="application/octet-stream"
    )

@app.route('/my_files')
def my_files():
    email = session.get('email')
    if not email:
        return redirect(url_for('index'))

    files = FileRecord.query.filter_by(user_email=email).order_by(FileRecord.id.desc()).all()
    return render_template('my_files.html', files=files)

@app.route('/logout')
def logout():
    Config.ATOM_AUTHENTICATION = False

    # Clear session keys
    session.pop('email', None)
    session.pop('token', None)
    session.pop('authenticated', None)  # If you have this flag

    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)