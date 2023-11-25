from flask import Flask, render_template, request, send_file, jsonify
import recog
import skimage
from PIL import Image
import numpy as np
import io
import json
import requests

app = Flask(__name__)


@app.route("/")
def home():
    return render_template('index.html')


@app.route("/perform-skin-recognition", methods=['GET', 'POST'])
def handle_recog():
    if request.method == "POST":
        # Nhận array options từ frontend
        selection = (request.form.getlist('sel[]'))

        # Nhận image từ frontend
        image = (request.files['image'])
        image = skimage.io.imread(image)
        try:
            res = recog.recognize(image, selection)
            image = Image.fromarray(image).resize((224, 224))
            content = []

            for i in res:
                img_arr = np.array(image)
                layer1, layer2, layer3 = img_arr[:, :,
                                                 0], img_arr[:, :, 1], img_arr[:, :, 2]
                mask = i["segment_data"]
                layer1, layer2, layer3 = (
                    layer1 * mask), (layer2 * mask), (layer3 * mask)
                layer0 = np.invert(np.dstack([layer1, layer2, layer3]))
                layer0[mask == 0] = 0
                filename = f"seg-{i['segment']}_pred-{i['prediction']}_conf-{i['confidence']}.jpg"
                content.append(
                    {"prediction": i['prediction'], "segment_data": filename, "confidence": i['confidence']})
                Image.fromarray(layer0.astype(np.uint8)).save(
                    f"test/{filename}.jpg")

            print(content)
            return jsonify(content)

        except Exception as e:
            return str(e)


@app.route('/images/<pid>.jpg')
def get_image(pid):
    pid = str(pid)
    img = skimage.io.imread(f"test/{pid}.jpg")
    img = Image.fromarray(img)
    file_object = io.BytesIO()
    img.save(file_object, 'JPEG')
    file_object.seek(0)
    return send_file(file_object, mimetype='image/JPEG')


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


if __name__ == "__main__":
    app.run("0.0.0.0", debug=True, port=5000)
