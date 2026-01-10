# AirMouse-AI-Image-Optimizer-Tool
AirMouse AI: Image Optimizer Tool

A sleek, Flask-powered web utility designed to prepare visual assets for the AirMouse AI project. This tool automates the tedious process of resizing, cropping, and compressing images to meet specific technical requirements for AI-driven applications.

🚀 Features

Smart 16:9 Cropping: Automatically centers and crops images to a cinematic 16:9 aspect ratio.

WebP Conversion: Converts standard formats (JPG, PNG, BMP) into the modern, highly efficient .webp format.

Size Constraint Logic: Intelligently compresses images to ensure the final file size is under 100KB without sacrificing significant visual quality.

Modern UI/UX: A dark-themed, responsive interface featuring drag-and-drop functionality and instant feedback.

Touchless Design: Built in the spirit of the AirMouse AI project—simple, fast, and efficient.

🛠️ Technology Stack

Backend: Python, Flask

Image Processing: Pillow (PIL)

Frontend: Tailwind CSS, JavaScript (Vanilla)

Icons: FontAwesome

📋 Installation

Clone the repository:

git clone [https://github.com/your-username/airmouse-image-tool.git](https://github.com/your-username/airmouse-image-tool.git)
cd airmouse-image-tool


Install dependencies:

pip install flask pillow


Run the application:

python app.py


Access the tool:
Open your browser and navigate to http://127.0.0.1:5000

🖥️ How it Works

Upload: Drag an image into the dashed zone or click to select a file.

Processing:

The backend calculates the center of your image to perform a 16:9 crop.

It converts the color space to RGB.

It runs an iterative loop, lowering the WebP quality and slightly shrinking dimensions until the file hits the <100KB target.

Download: Once the "Checkmark" appears, click the download button to save your optimized .webp file.

📄 License

This project is open-source and available under the MIT License.

Created as part of the AirMouse AI Project Ecosystem.
