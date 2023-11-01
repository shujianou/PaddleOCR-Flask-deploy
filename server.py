import os
import cv2
import time
import uuid
import json
from datetime import timedelta
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from paddleocr import PaddleOCR, draw_ocr

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(hours=1)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


def allowed_file(fname):
    return '.' in fname and fname.rsplit('.', 1)[1].lower() in ['png', 'jpg', 'jpeg']


@app.route("/")
def index():
    return render_template('index.html')


default_data = dict()
default_data['text'] = 'not supported img type'
default_data['p1'] = '0.0'
default_data['p2'] = '0.0'
default_data['p3'] = '0.0'
default_data['p4'] = '0.0'

ocr = PaddleOCR(use_angle_cls=True, use_gpu=False)  # 查看README的参数说明


def do_detect(file=None, return_coord=None):
    global ocr
    ext = file.filename.rsplit('.', 1)[1]
    random_name = '{}.{}'.format(uuid.uuid4().hex, ext)
    savepath = os.path.join('caches', secure_filename(random_name))
    file.save(savepath)
    img = cv2.imread(savepath)
    data = dict()
    data['text'] = ''
    try:
        img_result = ocr.ocr(img)
        for item in img_result[0]:
            point_data = item[0]
            data['text'] = item[1][0]
            if return_coord == '1':
                data['p1'] = point_data[0]
                data['p2'] = point_data[1]
                data['p3'] = point_data[2]
                data['p4'] = point_data[3]
    except:
        pass

    return data


@app.route('/ocr', methods=['POST', 'GET'])
def detect():
    files = request.files.getlist('files')
    # 是否返回坐标
    return_coord = request.args.get('return_coord')

    results = []
    if files:
        for file in files:
            if not allowed_file(file.filename):
                results.append(default_data)
                return
            results.append(do_detect(file=file, return_coord=return_coord))

    return jsonify(results)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9998, debug=False, threaded=True, processes=1)
    '''
    app.run()中可以接受两个参数，分别是threaded和processes，用于开启线程支持和进程支持。
    1.threaded : 多线程支持，默认为False，即不开启多线程;
    2.processes：进程数量，默认为1.
    '''
