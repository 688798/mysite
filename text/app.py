from flask import Flask, request, jsonify, send_file, render_template
from werkzeug.utils import secure_filename
import os
from paddleocr import PaddleOCR
from PIL import Image
import io

# 初始化Flask应用
app = Flask(__name__)#生成一个flask实例

# 设置允许的文件格式
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS    #检查文件是否在允许的扩展名中


# 初始化 OCR
ocr = PaddleOCR(use_angle_cls=True, lang="ch")


@app.route('/')   #定义主页路由，访问URL时返回html页面
def index():
    return render_template('index.html')


@app.route('/process_image', methods=['POST'])    #定义图片路由，只接受post请求
def process_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
#jsonify自动设置响应头，响应HTTP协议
    
    file = request.files['image']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        # 保存图片到内存中
        img_bytes = file.read()
        image = Image.open(io.BytesIO(img_bytes))

        # 运行 OCR
        result = ocr.ocr(img_bytes, cls=True)

        # 处理并返回结果
        ocr_results = []
        for idx in range(len(result)):
            res = result[idx]
            for line in res:
                text = line[1][0]  # 提取文本内容
                confidence = line[1][1]  # 提取置信度
                ocr_results.append(f"文本: {text}\n置信度: {confidence:.2f}\n\n")

        # 将结果发送回前端
        return jsonify({'results': ''.join(ocr_results)})


if __name__ == '__main__':
    app.run(debug=True)