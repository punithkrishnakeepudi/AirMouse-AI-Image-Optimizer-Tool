import os
import io
from flask import Flask, request, send_file, jsonify, render_template_string
from PIL import Image

app = Flask(__name__)

# Configuration
MAX_FILE_SIZE_KB = 100
TARGET_ASPECT_RATIO = 16 / 9

# Embedded HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AirMouse Image Optimizer</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .drag-active {
            border-color: #3b82f6 !important;
            background-color: rgba(59, 130, 246, 0.1) !important;
        }
        .loader {
            border-top-color: #3b82f6;
            -webkit-animation: spinner 1.5s linear infinite;
            animation: spinner 1.5s linear infinite;
        }
        @keyframes spinner {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body class="bg-slate-900 text-white h-screen flex flex-col items-center justify-center font-sans">

    <div class="w-full max-w-2xl p-6">
        <!-- Header -->
        <div class="text-center mb-10">
            <div class="flex justify-center mb-4">
                <i class="fa-solid fa-hand-pointer text-5xl text-blue-500"></i>
            </div>
            <h1 class="text-4xl font-bold mb-2">AirMouse Image Tool</h1>
            <p class="text-slate-400">Convert any image to WebP, 16:9 Ratio, < 100KB</p>
        </div>

        <!-- Upload Zone -->
        <div id="drop-zone" 
             class="border-2 border-dashed border-slate-600 rounded-xl bg-slate-800 p-10 text-center transition-all cursor-pointer hover:border-slate-400">

            <input type="file" id="file-input" class="hidden" accept="image/*">

            <div id="upload-content">
                <i class="fa-solid fa-cloud-arrow-up text-4xl text-slate-500 mb-4"></i>
                <h3 class="text-xl font-semibold mb-2">Drag & Drop or Click to Upload</h3>
                <p class="text-sm text-slate-500">Supports PNG, JPG, JPEG, BMP</p>
            </div>

            <!-- Loading State -->
            <div id="loading-content" class="hidden">
                <div class="loader ease-linear rounded-full border-4 border-t-4 border-slate-200 h-12 w-12 mb-4 mx-auto"></div>
                <h3 class="text-lg">Processing & Compressing...</h3>
            </div>
        </div>

        <!-- Result Area -->
        <div id="result-area" class="mt-8 hidden fade-in">
            <div class="bg-slate-800 rounded-lg p-4 flex items-center justify-between border border-slate-700">
                <div class="flex items-center space-x-4">
                    <div class="bg-green-500/20 text-green-400 p-3 rounded-full">
                        <i class="fa-solid fa-check"></i>
                    </div>
                    <div>
                        <h4 class="font-bold text-lg">Conversion Complete!</h4>
                        <p class="text-sm text-slate-400">16:9 Aspect Ratio • WebP • Optimized</p>
                    </div>
                </div>
                <button id="download-btn" class="bg-blue-600 hover:bg-blue-500 text-white px-6 py-2 rounded-lg font-semibold transition-colors flex items-center gap-2">
                    <i class="fa-solid fa-download"></i> Download
                </button>
            </div>
        </div>

        <!-- Error Area -->
        <div id="error-area" class="mt-8 hidden">
            <div class="bg-red-500/20 border border-red-500/50 text-red-200 p-4 rounded-lg text-center">
                <p id="error-msg">Something went wrong.</p>
            </div>
        </div>
    </div>

    <script>
        const dropZone = document.getElementById('drop-zone');
        const fileInput = document.getElementById('file-input');
        const uploadContent = document.getElementById('upload-content');
        const loadingContent = document.getElementById('loading-content');
        const resultArea = document.getElementById('result-area');
        const downloadBtn = document.getElementById('download-btn');
        const errorArea = document.getElementById('error-area');
        const errorMsg = document.getElementById('error-msg');

        // Drag and Drop Events
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, preventDefaults, false);
        });

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, highlight, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, unhighlight, false);
        });

        function highlight(e) {
            dropZone.classList.add('drag-active');
        }

        function unhighlight(e) {
            dropZone.classList.remove('drag-active');
        }

        // Handle Drops and Clicks
        dropZone.addEventListener('drop', handleDrop, false);
        dropZone.addEventListener('click', () => fileInput.click());
        fileInput.addEventListener('change', (e) => handleFiles(e.target.files));

        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            handleFiles(files);
        }

        function handleFiles(files) {
            if (files.length > 0) {
                uploadFile(files[0]);
            }
        }

        let currentDownloadBlob = null;

        function uploadFile(file) {
            // UI Reset
            errorArea.classList.add('hidden');
            resultArea.classList.add('hidden');
            uploadContent.classList.add('hidden');
            loadingContent.classList.remove('hidden');

            const formData = new FormData();
            formData.append('file', file);

            fetch('/convert', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (!response.ok) throw new Error('Conversion failed');
                return response.blob();
            })
            .then(blob => {
                // Success
                loadingContent.classList.add('hidden');
                uploadContent.classList.remove('hidden');
                resultArea.classList.remove('hidden');

                // Create download URL
                if (currentDownloadBlob) window.URL.revokeObjectURL(currentDownloadBlob);
                currentDownloadBlob = window.URL.createObjectURL(blob);

                downloadBtn.onclick = () => {
                    const a = document.createElement('a');
                    a.href = currentDownloadBlob;
                    a.download = 'airmouse_optimized.webp';
                    document.body.appendChild(a);
                    a.click();
                    a.remove();
                };
            })
            .catch(error => {
                loadingContent.classList.add('hidden');
                uploadContent.classList.remove('hidden');
                errorMsg.textContent = "Error: " + error.message;
                errorArea.classList.remove('hidden');
            });
        }
    </script>
</body>
</html>
"""


def crop_center_16_9(img):
    """
    Crops the image to a 16:9 aspect ratio from the center.
    """
    img_width, img_height = img.size
    current_ratio = img_width / img_height

    if current_ratio == TARGET_ASPECT_RATIO:
        return img

    if current_ratio > TARGET_ASPECT_RATIO:
        # Image is too wide, crop width
        new_width = int(img_height * TARGET_ASPECT_RATIO)
        offset = (img_width - new_width) // 2
        return img.crop((offset, 0, offset + new_width, img_height))
    else:
        # Image is too tall, crop height
        new_height = int(img_width / TARGET_ASPECT_RATIO)
        offset = (img_height - new_height) // 2
        return img.crop((0, offset, img_width, offset + new_height))


def compress_image(image):
    """
    Compresses image to WebP < 100KB while maintaining 16:9 aspect ratio.
    """
    # 1. Convert to RGB (in case of RGBA/PNG)
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")

    # 2. Crop to 16:9
    image = crop_center_16_9(image)

    # 3. Resize if the image is massive (helps with size limit)
    # A max width of 1920 (Full HD) is a good starting point for web images
    if image.width > 1920:
        new_height = int(1920 / TARGET_ASPECT_RATIO)
        image = image.resize((1920, new_height), Image.Resampling.LANCZOS)

    img_io = io.BytesIO()
    quality = 95  # Start with high quality

    # 4. Iterative compression loop
    while True:
        img_io.seek(0)
        img_io.truncate()
        image.save(img_io, 'WEBP', quality=quality)

        size_kb = img_io.tell() / 1024

        if size_kb <= MAX_FILE_SIZE_KB or quality <= 10:
            break

        # Reduce quality
        quality -= 5

        # If quality is dropping too low, shrink dimensions instead
        if quality < 50:
            width, height = image.size
            image = image.resize((int(width * 0.9), int(height * 0.9)), Image.Resampling.LANCZOS)
            quality = 80  # Reset quality for the smaller image

    img_io.seek(0)
    return img_io


@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route('/convert', methods=['POST'])
def convert_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        image = Image.open(file.stream)
        compressed_io = compress_image(image)

        return send_file(
            compressed_io,
            mimetype='image/webp',
            as_attachment=True,
            download_name='airmouse_optimized.webp'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
