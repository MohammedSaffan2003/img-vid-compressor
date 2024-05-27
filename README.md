# Image and Video Compression

This project is a web application that allows users to upload and compress images (JPEG, PNG) and videos (MP4) using standard algorithms. The compressed files can then be downloaded.

## Features

- Upload images and videos
- Compress images using JPEG compression
- Compress videos using H.264 compression
- Download compressed files

## Technologies Used

- Python
- Flask
- HTML/CSS
- Pillow (for image processing)
- MoviePy (for video processing)

## Setup

1. Clone the repository:


2. Create a virtual environment and install dependencies:

python -m venv venv
source venv/bin/activate # On Windows use venv\Scripts\activate
pip install -r requirements.txt


3. Run the application:

python app.py


4. Open your web browser and navigate to `http://127.0.0.1:5000/`.

## Usage

- Select an image or video file to upload.
- Click the "Upload and Compress" button.
- The compressed file will be available for download.

## License

This project is licensed under the MIT License.
