from flask import Flask, render_template, request, send_from_directory, redirect, url_for
import os
from PIL import Image
import moviepy.editor as mp

# app = Flask(__name__)
# app.config['UPLOAD_FOLDER'] = 'uploads'
# app.config['COMPRESSED_FOLDER'] = 'compressed'

# if not os.path.exists(app.config['UPLOAD_FOLDER']):
#     os.makedirs(app.config['UPLOAD_FOLDER'])

# if not os.path.exists(app.config['COMPRESSED_FOLDER']):
#     os.makedirs(app.config['COMPRESSED_FOLDER'])

# def format_size(size):
#     for unit in ['bytes', 'KB', 'MB', 'GB']:
#         if size < 1024:
#             return f"{size:.2f} {unit}"
#         size /= 1024
#     return f"{size:.2f} TB"

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/upload', methods=['POST'])
# def upload_file():
#     if 'file' not in request.files:
#         return redirect(request.url)
    
#     file = request.files['file']
#     if file.filename == '':
#         return redirect(request.url)
    
#     if file:
#         file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
#         file.save(file_path)
#         return render_template('index.html', filename=file.filename, filesize=format_size(os.path.getsize(file_path)))

# @app.route('/uploads/<filename>')
# def uploaded_file(filename):
#     return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# @app.route('/compress', methods=['POST'])
# def compress_file():
#     filename = request.form['filename']
#     file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#     compressed_path = os.path.join(app.config['COMPRESSED_FOLDER'], filename)
    
#     if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
#         image = Image.open(file_path)
#         image.save(compressed_path, optimize=True, quality=85)
#     elif filename.lower().endswith(('.mp4', '.avi', '.mov')):
#         video = mp.VideoFileClip(file_path)
#         video.write_videofile(compressed_path, bitrate="500k")
    
#     return render_template('index.html', filename=filename, compressed_filename=filename, filesize=format_size(os.path.getsize(file_path)), compressed_size=format_size(os.path.getsize(compressed_path)))

# @app.route('/compressed/<filename>')
# def compressed_file(filename):
#     return send_from_directory(app.config['COMPRESSED_FOLDER'], filename)

# if __name__ == '__main__':
#     app.run(debug=True)




from flask import Flask, render_template, request, send_file, redirect, url_for
import os
from werkzeug.utils import secure_filename
from PIL import Image
import cv2

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
COMPRESSED_FOLDER = 'compressed'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['COMPRESSED_FOLDER'] = COMPRESSED_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(COMPRESSED_FOLDER):
    os.makedirs(COMPRESSED_FOLDER)

def compress_image(image_path, output_path):
    img = Image.open(image_path)
    img.save(output_path, optimize=True, quality=60)

def compress_video(video_path, output_path):
    cap = cv2.VideoCapture(video_path)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_path, fourcc, 20.0, (int(cap.get(3)), int(cap.get(4))))

    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            out.write(frame)
        else:
            break

    cap.release()
    out.release()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    file_size = os.path.getsize(file_path)
    file_size_kb = file_size / 1024

    return render_template('index.html', filename=filename, uploaded=True, file_size=file_size_kb)

@app.route('/compress', methods=['POST'])
def compress_file():
    filename = request.form['filename']
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    compressed_file_path = os.path.join(app.config['COMPRESSED_FOLDER'], filename)

    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        compress_image(file_path, compressed_file_path)
    elif filename.lower().endswith(('.mp4', '.avi', '.mov')):
        compress_video(file_path, compressed_file_path)

    compressed_file_size = os.path.getsize(compressed_file_path)
    compressed_file_size_kb = compressed_file_size / 1024

    return render_template('index.html', filename=filename, compressed=True, compressed_filename=filename, compressed_size=compressed_file_size_kb)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))

@app.route('/compressed/<filename>')
def compressed_file(filename):
    return send_file(os.path.join(app.config['COMPRESSED_FOLDER'], filename))

@app.route('/download/<filename>')
def download_file(filename):
    compressed_file_path = os.path.join(app.config['COMPRESSED_FOLDER'], filename)
    return send_file(compressed_file_path, as_attachment=True)

@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    # Delete both the original and compressed files
    original_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    compressed_file_path = os.path.join(app.config['COMPRESSED_FOLDER'], filename)

    if os.path.exists(original_file_path):
        os.remove(original_file_path)
    if os.path.exists(compressed_file_path):
        os.remove(compressed_file_path)

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
