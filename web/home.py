from flask import Flask, render_template, request, send_file, jsonify, redirect
import recog
import skimage.io
from PIL import Image
import numpy as np
import io
import os
import requests
import uuid
import datetime
import firebase_admin
from firebase_admin import firestore

# connect to db
creds = firebase_admin.credentials.Certificate("firebase_creds.json")
default_app = firebase_admin.initialize_app(creds)
firestore = firestore.client()

# webapp start
app = Flask(__name__)

# stores sessionID
currentUser = {
    '1234': {
        'name': "test",
        'exptime': int((datetime.datetime.now() + datetime.timedelta(minutes=5)).timestamp()),
    }
}

@app.route('/', methods=["POST", "GET"])
def source():
    if (request.method == "POST"):
        sessionID = request.json.get('sessionID')
        try:
            user = currentUser[str(sessionID)]
            if (int(user['exptime']) > int(datetime.datetime.now().timestamp())):
                return jsonify({'status': 'true'})
            else:
                return jsonify({'status': 'false', 'reason': 'expired'})
        except Exception as e:
                return jsonify({'status': 'false', 'reason': 'notfound'})

    elif (request.method == "GET"):
        return render_template('source.html')

# authenticate
@app.route('/login', methods=["GET", "POST"])
def login():
    if (request.method == "GET"):
        return render_template('login.html')
    elif (request.method == "POST"):
        action = request.json.get("action")
        if (action == "login"):
            username = request.json.get("username")
            password = request.json.get("password")
            userbase = firestore.collection('users').get().to_dict()
            for key, value in userbase.iteritems():
                if (value["password"] == password and value["username"] == username):
                    sessionID = uuid.uuid4().hex
                    currentUser[str(sessionID)] = {
                        "name": value["name"],
                        "userID": key,
                        "role": value["role"]
                    }
                    return jsonify({
                        "status": "true", 
                        "data": {
                            "name": value["name"],
                            "userID": key,
                            "role": value["role"]
                        }
                    })
            return jsonify({"status": "false"})
        elif (action == "register"):
            name = request.json.get("name")
            username = request.json.get("username")
            password = request.json.get("password")
            role = request.json.get("role")
            userbase = firestore.collection('users')
            userbase.document(uuid.uuid4().hex).set({
                "name": name,
                "username": username,
                "password": password,
                "role": role
            })
            return jsonify({"status": "true"})
        else:
            return False

# home for real
@app.route("/home")
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)