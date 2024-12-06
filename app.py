from flask import Flask, render_template, request, send_file, jsonify
from io import BytesIO
from PIL import Image, ImageOps
import requests
from rembg import remove
import os

app = Flask(__name__)
port = int(os.environ.get("PORT", 8000))
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/remove-background', methods=['POST'])
def remove_background():
    if 'image' not in request.files or 'background' not in request.form:
        return jsonify({"error": "Image and background data are required."}), 400

    try:
        # Retrieve the uploaded image
        file = request.files['image']
        file.seek(0)
        input_image = Image.open(file)

        if input_image.format not in ['JPEG', 'PNG']:
            return jsonify({"error": "Unsupported image format. Please upload JPEG or PNG files."}), 400

        file.seek(0)
        output_image_bytes = remove(file.read())

        # Create an image from the processed bytes
        foreground_image = Image.open(BytesIO(output_image_bytes)).convert("RGBA")

        # Retrieve the background image
        background_url = request.form['background']
        response = requests.get(background_url)
        response.raise_for_status()
        background_image = Image.open(BytesIO(response.content)).convert("RGBA")

        # Resize background to match foreground
        background_image = background_image.resize(foreground_image.size, Image.Resampling.LANCZOS)

        # Combine images
        combined_image = Image.alpha_composite(background_image, foreground_image)

        # Save the combined image to a buffer
        buffer = BytesIO()
        combined_image.save(buffer, format="PNG", optimize=True)
        buffer.seek(0)

        return send_file(buffer, mimetype='image/png', as_attachment=False, download_name="combined_image.png")

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An error occurred while processing the image."}), 500

if __name__ == "__main__":
       port = int(os.environ.get("PORT", 5000))
       app.run(host="0.0.0.0", port=port)