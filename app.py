import os
from flask import Flask, request, send_file, render_template
from io import BytesIO
from PIL import Image
from nudenet.nudenet import NudeDetector,nsfw

app = Flask(__name__)
detector = NudeDetector(providers=['AzureExecutionProvider', 'CPUExecutionProvider'])

def remove_nsfw(image, method, overlay):
    nudes = detector.censor(image=image, censor=nsfw, method=method, overlay=overlay)
    img_io = BytesIO()
    nudes.output.save(img_io, 'JPEG')
    img_io.seek(0)
    return img_io

@app.route('/upload', methods=['POST'])
def upload_image():
    try:
        if 'file' not in request.files or 'method' not in request.form:
            return "Missing required fields", 400
        file = request.files['file']
        method = request.form['method'].replace('_', ' ')
        overlay = request.files['overlay']
        if file.filename == '':
            return "No selected file", 400
        overlay = None
        if 'overlay' in request.files and request.files['overlay'].filename != '':
            overlay_image = Image.open(request.files['overlay'].stream)
            overlay_image.save('overlay.png', 'PNG')
            overlay = 'overlay.png'
        if file:
            input = Image.open(file.stream)
            processed_image = remove_nsfw(input, method, overlay)
            return send_file(processed_image, mimetype='image/jpeg')
        if overlay:
            os.remove(overlay)
    except Exception as e:
        print(repr(e))
        return "An error occurred", 500
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)