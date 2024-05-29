import os
from flask import Flask, request, redirect, url_for, render_template, send_from_directory, send_file
from werkzeug.utils import secure_filename
from PIL import Image

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'  # Folder to store uploaded files
COMPRESSED_FOLDER = 'compressed'  # Folder to store compressed files
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'mp4', 'avi', 'mov'}  # Allowed file extensions

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['COMPRESSED_FOLDER'] = COMPRESSED_FOLDER

# Ensure upload and compressed folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(COMPRESSED_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if a file is allowed based on its extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def compress_image(image_path, output_path, quality=60):
    """Compress an image and save it to the output path with the specified quality."""
    img = Image.open(image_path)
    if img.mode == 'RGBA':
        img = img.convert('RGB')  # Convert RGBA to RGB to save as JPEG
    img.save(output_path, "JPEG", quality=quality)  # Save the image with the specified quality

@app.route('/')
def index():
    """Render the home page."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and save the file to the uploads folder."""
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        file_size = os.path.getsize(file_path) / 1024.0  # File size in KB
        return render_template('index.html', filename=filename, uploaded=True, file_size=file_size)
    return redirect(request.url)

@app.route('/compress', methods=['POST'])
def compress_file():
    """Compress the uploaded file and save it to the compressed folder."""
    filename = request.form['filename']
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    compressed_file_path = os.path.join(app.config['COMPRESSED_FOLDER'], filename)

    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        compress_image(file_path, compressed_file_path)  # Compress the image
    elif filename.lower().endswith(('.mp4', '.avi', '.mov')):
        os.system(f'ffmpeg -i {file_path} -vcodec libx264 {compressed_file_path}')  # Compress the video

    compressed_size = os.path.getsize(compressed_file_path) / 1024.0  # Compressed size in KB

    return render_template('index.html', filename=filename, uploaded=True, file_size=os.path.getsize(file_path) / 1024.0,
                           compressed_filename=filename, compressed=True, compressed_size=compressed_size)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve the uploaded file."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/compressed/<filename>')
def compressed_file(filename):
    """Serve the compressed file."""
    return send_from_directory(app.config['COMPRESSED_FOLDER'], filename)

@app.route('/download/<filename>')
def download_file(filename):
    """Provide a download link for the compressed file."""
    compressed_file_path = os.path.join(app.config['COMPRESSED_FOLDER'], filename)
    return send_file(compressed_file_path, as_attachment=True)

@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    """Delete the compressed file."""
    compressed_file_path = os.path.join(app.config['COMPRESSED_FOLDER'], filename)
    if os.path.exists(compressed_file_path):
        os.remove(compressed_file_path)  # Remove the file if it exists
    # Delete the uploaded file also if it exists
    upload_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(upload_file_path):
        os.remove(upload_file_path)  # Remove the file if it exists
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)

"""
Function Definitions and Working:

1. allowed_file(filename):
   - Purpose: Checks if the uploaded file's extension is allowed.
   - Working: It splits the filename by the last dot and checks if the extension is in the allowed extensions.

2. compress_image(image_path, output_path, quality=60):
   - Purpose: Compresses an image using the Pillow library.
   - Working: Opens the image from the given path, converts it to RGB if it has an alpha channel, then saves it with the specified quality to the output path.

3. index():
   - Purpose: Renders the home page.
   - Working: Returns the index.html template.

4. upload_file():
   - Purpose: Handles file upload.
   - Working: Checks if a file is part of the request, secures the filename, saves the file to the upload folder, and renders the template with file details.

5. compress_file():
   - Purpose: Compresses the uploaded file (image or video).
   - Working: Depending on the file type, it compresses the image using Pillow or the video using ffmpeg, then renders the template with compressed file details.

6. uploaded_file(filename):
   - Purpose: Serves the uploaded file.
   - Working: Sends the file from the upload directory.

7. compressed_file(filename):
   - Purpose: Serves the compressed file.
   - Working: Sends the file from the compressed directory.

8. download_file(filename):
   - Purpose: Allows downloading of the compressed file.
   - Working: Sends the compressed file as an attachment.

9. delete_file(filename):
   - Purpose: Deletes the compressed file.
   - Working: Checks if the file exists and removes it, then redirects to the home page.
"""
