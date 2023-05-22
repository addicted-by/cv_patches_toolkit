from flask import Flask, render_template, request, jsonify
import cv2
import base64
import numpy as np
import io

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'


@app.route('/')
def index():
    return render_template('index.html')
 

# @app.route('/annotate', methods=['POST'])
# def annotate():
#     image_data = request.form['imageData']
#     drawing_mode = request.form['drawingMode']
#     polylines = request.form.getlist('polylines[]')
#     rectangle = request.form.get('rectangle')

#     image_path = save_image(image_data)
#     image = cv2.imread(image_path)

#     if drawing_mode == 'rectangle':
#         rectangle = parse_rectangle(rectangle)
#         cv2.rectangle(image, rectangle[0], rectangle[1], (0, 0, 255), 2)
#     elif drawing_mode == 'polylines':
#         polylines = parse_polylines(polylines)
#         for polyline in polylines:
#             pts = np.array(polyline, np.int32)
#             pts = pts.reshape((-1, 1, 2))
#             cv2.polylines(image, [pts], True, (0, 0, 255), 2)

#     result = encode_image(image)
#     return jsonify({'imageData': result})


# def save_image(image_data):
#     image_data = image_data.split(",")[1]
#     image_bytes = base64.b64decode(image_data)
#     image_path = f"{app.config['UPLOAD_FOLDER']}/image.jpg"

#     with open(image_path, 'wb') as f:
#         f.write(image_bytes)

#     return image_path


# def encode_image(image):
#     _, buffer = cv2.imencode('.jpg', image)
#     image_data = base64.b64encode(buffer)
#     return image_data.decode('utf-8')


# def parse_rectangle(rectangle):
#     rectangle = rectangle.split(',')
#     return ((int(rectangle[0]), int(rectangle[1])),
#             (int(rectangle[2]), int(rectangle[3])))


# def parse_polylines(polylines):
#     parsed_polylines = []
#     for polyline in polylines:
#         points = polyline.split(',')
#         parsed_polylines.append([(int(points[i]), int(points[i+1])) for i in range(0, len(points), 2)])
#     return parsed_polylines


if __name__ == '__main__':
    app.run()
