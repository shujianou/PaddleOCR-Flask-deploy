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


@app.route('/ocr', methods=['POST', 'GET'])
def detect():
    file = request.files['file']
    # 是否返回坐标
    return_coord = request.args.get('return_coord')

    if file and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1]
        random_name = '{}.{}'.format(uuid.uuid4().hex, ext)
        savepath = os.path.join('caches', secure_filename(random_name))
        file.save(savepath)
        img = cv2.imread(savepath)
        img_result = ocr.ocr(img)
        '''
        识别结果将以列表返回在img_result，根据具体需求进行改写
        '''
        results = []
        for item in img_result[0]:
            point_data = item[0]
            data = dict()
            data['text'] = item[1][0]
            if return_coord == '1':
                data['p1'] = point_data[0]
                data['p2'] = point_data[1]
                data['p3'] = point_data[2]
                data['p4'] = point_data[3]

            results.append(data)

        return jsonify(results)
    return jsonify({'服务状态': 'faild'})


if __name__ == '__main__':
    ocr = PaddleOCR(use_angle_cls=True, use_gpu=False)  # 查看README的参数说明
    app.run(host='0.0.0.0', port=9998, debug=False, threaded=True, processes=1)
    '''
    app.run()中可以接受两个参数，分别是threaded和processes，用于开启线程支持和进程支持。
    1.threaded : 多线程支持，默认为False，即不开启多线程;
    2.processes：进程数量，默认为1.
    '''
