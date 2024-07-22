from flask import Flask, render_template, request, send_file, jsonify
import recog
import skimage.io
from PIL import Image
import numpy as np
import io
import os
import requests

app = Flask(__name__)

@app.route("/")
def home():
    return render_template('home.html')

# Path to the folders containing images
HISTORY_FOLDER = os.path.join(app.root_path, 'history')
TEST_FOLDER = os.path.join(app.root_path, 'test')
SEGMENTS_FOLDER = os.path.join(app.root_path, 'segments')

@app.route('/save-image', methods=['POST'])
def save_image():
    if 'image' not in request.files:
        return jsonify({"error": "No image part in the request"}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if not os.path.exists(HISTORY_FOLDER):
        os.makedirs(HISTORY_FOLDER)

    # Number of images in the history folder
    image_count = len([name for name in os.listdir(HISTORY_FOLDER) if os.path.isfile(os.path.join(HISTORY_FOLDER, name))])

    # Save image with a new name
    file_path = os.path.join(HISTORY_FOLDER, f"{image_count + 1}.jpg")
    file.save(file_path)

    return jsonify({"message": "Image saved successfully", "filename": f"{image_count + 1}.jpg"}), 200

@app.route('/perform-skin-recognition', methods=['POST'])
def handle_recog():
    # Receive array options from frontend
    selection = request.form.get("sel").split(",")
    print(selection)
    if 'healthy' not in selection: 
        selection.append("healthy")
        
    # Receive filename from frontend
    filename = request.form.get('filename')

    # Path to the original image
    image_path = os.path.join(HISTORY_FOLDER, filename)
    image = skimage.io.imread(image_path)

    res = recog.recognize(image, selection)

    # Save superpixel image
    superpixel_path = os.path.join(TEST_FOLDER, filename)
    superpixel_img = Image.fromarray(res['superpixel'])
    superpixel_img.save(superpixel_path)

    # Save the segments images
    segment_folder = os.path.join(SEGMENTS_FOLDER, filename.split('.')[0])
    if not os.path.exists(segment_folder):
        os.makedirs(segment_folder)
    for i, segment in enumerate(res['segments']):
        class_name = segment['prediction']
        confidence = segment['confidence']
        segment_path = os.path.join(segment_folder, f"{i}_{class_name}_{confidence}.jpg")
        segment_img = Image.fromarray(segment['image'])
        segment_img.save(segment_path)

        # Save the image path in the response
        segment['image'] = f"{i}_{class_name}_{confidence}.jpg"

    return jsonify(res['segments'])

@app.route('/images/<filename>')
def get_image(filename):
    img_path = os.path.join(TEST_FOLDER, filename)
    img = skimage.io.imread(img_path)
    img = Image.fromarray(img)
    file_object = io.BytesIO()
    img.save(file_object, 'JPEG')
    file_object.seek(0)
    return send_file(file_object, mimetype='image/jpeg')

@app.route('/images/<folder>/<filename>')
def get_segment_image(folder, filename):
    img_path = os.path.join(SEGMENTS_FOLDER, folder, filename)
    img = skimage.io.imread(img_path)
    img = Image.fromarray(img)
    file_object = io.BytesIO()
    img.save(file_object, 'JPEG')
    file_object.seek(0)
    return send_file(file_object, mimetype='image/jpeg')


@app.route("/askGPT", methods=['POST'])
def chatGPT():
    def chatGPT(ques):
        url = "https://chatgpt-api8.p.rapidapi.com/"

        payload = [
            {
                "content": "Hello! I'm an AI assistant bot based on ChatGPT 3. How may I help you?",
                "role": "system"
            },
            {
                "content": f"{ques}",
                "role": "user"
            }
        ]
        headers = {
            "content-type": "application/json",
            "X-RapidAPI-Key": "030c80dc47mshbe06ccceee3100cp18b554jsnc6867b4f1b65",
            "X-RapidAPI-Host": "chatgpt-api8.p.rapidapi.com"
        }
        # huytrongnghia: 8dd3bfa3f3mshda3845149bb330ep1c4505jsna147eee499b5
        # khkt: d89a8977f9mshd28e97843a01cf2p158370jsn0cb69019b238
        # huynghia: 8eacc0c16dmshb79a0fe65bc3344p14e02ajsn29bf84e2e8b9
        # huytrong: 030c80dc47mshbe06ccceee3100cp18b554jsnc6867b4f1b65
        # nguyenquynh: 0c6c1ec218msh58fce662b00a268p1e2172jsn77027176568f

        response = requests.post(url, json=payload, headers=headers)
        data = response.json()

        return data["text"]

    try:
        data = request.json
        user_message = data['message']

        # Call your ChatGPT function here
        bot_message = chatGPT(user_message)

        return jsonify({'content': bot_message})
    except Exception as e:
        return jsonify({'error': str(e)})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    

# cấu trúc thư mục:
# 
# ├── backend.py 
# ├── recog.py                        
# ├── static/                        
# │   ├── style.css                  
# │   └── script.js      
# │   └── images/               
# ├── templates/                     
# │   └── home.html                 
# ├── history/                     
# ├── segments/               # chứa những thư mục ảnh nhỏ hơn 
# └── test/
