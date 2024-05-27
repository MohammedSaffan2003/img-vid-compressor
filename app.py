from flask import Flask, render_template, request, send_from_directory, redirect, url_for
import os
from PIL import Image
import moviepy.editor as mp

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['COMPRESSED_FOLDER'] = 'compressed'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

if not os.path.exists(app.config['COMPRESSED_FOLDER']):
    os.makedirs(app.config['COMPRESSED_FOLDER'])

def format_size(size):
    for unit in ['bytes', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} TB"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    
    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        return render_template('index.html', filename=file.filename, filesize=format_size(os.path.getsize(file_path)))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/compress', methods=['POST'])
def compress_file():
    filename = request.form['filename']
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    compressed_path = os.path.join(app.config['COMPRESSED_FOLDER'], filename)
    
    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        image = Image.open(file_path)
        image.save(compressed_path, optimize=True, quality=85)
    elif filename.lower().endswith(('.mp4', '.avi', '.mov')):
        video = mp.VideoFileClip(file_path)
        video.write_videofile(compressed_path, bitrate="500k")
    
    return render_template('index.html', filename=filename, compressed_filename=filename, filesize=format_size(os.path.getsize(file_path)), compressed_size=format_size(os.path.getsize(compressed_path)))

@app.route('/compressed/<filename>')
def compressed_file(filename):
    return send_from_directory(app.config['COMPRESSED_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
