from flask import Flask, request, render_template, send_file, redirect, url_for
from PIL import Image
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

def encode_message(img, msg):
    length = len(msg)
    if length > 255:
        raise ValueError("Message is too long to encode in the image")

    encoded = img.copy()
    width, height = img.size
    index = 0
    
    for row in range(height):
        for col in range(width):
            r, g, b = img.getpixel((col, row))
            if row == 0 and col == 0:
                r = length
            elif index < length:
                r = ord(msg[index])
                index += 1
            encoded.putpixel((col, row), (r, g, b))
    return encoded

def decode_message(img):
    width, height = img.size
    msg = ''
    length = img.getpixel((0, 0))[0]
    
    for row in range(height):
        for col in range(width):
            if row == 0 and col == 0:
                continue
            if len(msg) < length:
                r, g, b = img.getpixel((col, row))
                msg += chr(r)
    return msg

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/encode', methods=['POST'])
def encode():
    if 'image' not in request.files or 'message' not in request.form:
        return redirect(request.url)
    
    image = request.files['image']
    message = request.form['message']
    if image.filename == '':
        return redirect(request.url)
    
    img = Image.open(image)
    encoded_img = encode_message(img, message)
    encoded_path = os.path.join(app.config['UPLOAD_FOLDER'], 'encoded.png')
    encoded_img.save(encoded_path)
    
    return render_template('result.html', image_path=encoded_path)

@app.route('/decode', methods=['POST'])
def decode():
    if 'image' not in request.files:
        return redirect(request.url)
    
    image = request.files['image']
    if image.filename == '':
        return redirect(request.url)
    
    img = Image.open(image)
    hidden_message = decode_message(img)
    
    return render_template('result.html', hidden_message=hidden_message)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
