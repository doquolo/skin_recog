from flask import Flask, render_template, request, send_file, jsonify
from PIL import Image, ImageOps
import numpy as np
from skimage.segmentation import slic, mark_boundaries
from skimage.util import img_as_float
from tensorflow import keras

import matplotlib
import io 
matplotlib.use('Agg')  # Sử dụng backend Agg để tránh lỗi RuntimeError

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

app = Flask(__name__)

# Load the pre-trained model
model = keras.models.load_model('models/keras_model_2.h5')

# Load the labels
class_names = ['thủy đậu', 'chàm', 'ung thư da', 'khỏe mạnh']

def predict_with_model(img, seg):
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

    image = img.convert("RGB")

    size = (224, 224)
    image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)

    image_array = np.asarray(image)
    normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1

    data[0] = normalized_image_array

    prediction = model.predict(data)
    index = np.argmax(prediction)
    class_name = class_names[index]
    confidence_score = prediction[0][index]

    return {"class_name": class_name, "confidence": confidence_score}

def recognize(img):
    pathSave = 'segments/'

    skin_image = Image.fromarray(img).resize((224, 224))
    segments = slic(img_as_float(skin_image), n_segments=4, sigma=5)

    fig = Figure()  # Tạo đối tượng Figure mới
    canvas = FigureCanvas(fig)  # Tạo canvas cho Figure

    ax = fig.add_subplot(1, 1, 1)
    ax.imshow(mark_boundaries(img_as_float(skin_image), segments, background_label=0, mode='thick'))
    ax.axis("off")
    
    canvas.draw()  # Vẽ canvas
    

    # Lưu figure vào file ảnh
    canvas.print_png("test/.superpixels.png")
    image = Image.open('test/.superpixels.png')
    image.convert('RGB').save('test/.superpixels.jpg', 'JPEG')

    res = []

    segNum = 0
    for (i, segVal) in enumerate(np.unique(segments)):
        temp_i = i
        mask = np.zeros(skin_image.size[:2], dtype="uint8")
        mask[segments == segVal] = 255
        extracted_mask = np.stack(np.nonzero(mask), axis=-1)
        im = Image.fromarray(mask)
        cropped_segment = im.crop((min(extracted_mask[:, 1]), min(
            extracted_mask[:, 0]), max(extracted_mask[:, 1]), max(extracted_mask[:, 0])))
        cropped_img_segment = skin_image.crop((min(extracted_mask[:, 1]), min(
            extracted_mask[:, 0]), max(extracted_mask[:, 1]), max(extracted_mask[:, 0])))
        temp = np.array(cropped_segment) / 255
        output = np.array(cropped_img_segment)

        for i in range(3):
            final_result = np.multiply(
                temp, (np.array(cropped_img_segment)[:, :, i]))
            output[:, :, i] = final_result
        final_seg = Image.fromarray(output)

        out = predict_with_model(final_seg, temp_i)

        res.append({"segment": temp_i, "prediction": out['class_name'], "confidence": str(round(out['confidence']*100)), "segment_data": mask})
        Image.fromarray(mask).save(f"segments/seg-{temp_i}_pred-{out['class_name']}_conf-{round(out['confidence'], 3)}.jpg")
            
        print(f"seg-{temp_i}_pred-{out['class_name']} \nConfidence: {round(out['confidence'], 3)}")

    return res
