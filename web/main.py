from flask import Flask, render_template, request, send_file, jsonify
import recog
import skimage
from PIL import Image
import numpy as np
import io
import json

app = Flask(__name__)


@app.route("/")
def home():
    return render_template('index.html')


@app.route("/perform-skin-recognition", methods=['GET', 'POST'])
def handle_recog():
    if request.method == "POST":
        selection = (request.form.getlist('sel[]'))
        print(selection)
        image = (request.files['image'])
        image = skimage.io.imread(image)
        try:
            res = recog.recognize(image)
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


if __name__ == "__main__":
    app.run()
