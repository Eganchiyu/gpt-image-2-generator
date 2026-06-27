import os
import base64
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 3840 * 2160  # 50MB

client = OpenAI(
    api_key="***REDACTED***",
    base_url="https://api.rua.chat/v1"
)

ALLOWED_EXT = {'png', 'jpg', 'jpeg', 'webp', 'gif'}
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'outputs')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_image():
    try:
        prompt = request.form.get('prompt', '')
        if not prompt:
            return jsonify({'error': '请输入图像描述'}), 400

        files = request.files.getlist('images')
        mask_file = request.files.get('mask')
        mode = request.form.get('mode', 'edit')  # 生图模式 / 改图模式
        image_files = []
        for f in files:
            if f and f.filename and allowed_file(f.filename):
                image_files.append(f)

        if image_files:
            if mode == 'generate':
                # 生图模式：多张参考图全部上传
                image_tuples = [
                    (f.filename, f.read(), f.content_type or 'image/png')
                    for f in image_files
                ]
                response = client.images.edit(
                    model="gpt-image-2",
                    prompt=prompt,
                    image=image_tuples if len(image_tuples) > 1 else image_tuples[0],
                    n=1,
                    size="auto",
                    response_format="b64_json"
                )
            else:
                # 改图模式：1张图 + 可选 mask
                ref = image_files[0]
                image_tuple = (ref.filename, ref.read(), ref.content_type or 'image/png')

                kwargs = dict(
                    model="gpt-image-2",
                    prompt=prompt,
                    image=image_tuple,
                    n=1,
                    size="auto",
                    response_format="b64_json"
                )

                # 可选 mask
                if mask_file and mask_file.filename and allowed_file(mask_file.filename):
                    kwargs['mask'] = (
                        mask_file.filename,
                        mask_file.read(),
                        mask_file.content_type or 'image/png'
                    )

                response = client.images.edit(**kwargs)
        else:
            # 无参考图：纯文本生成
            response = client.images.generate(
                model="gpt-image-2",
                prompt=prompt,
                n=1,
                size="auto",
                response_format="b64_json"
            )

        image_data = response.data[0]

        if hasattr(image_data, 'b64_json') and image_data.b64_json:
            image_url = f"data:image/png;base64,{image_data.b64_json}"
            # 保存到本地
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            filename = datetime.now().strftime('%Y%m%d_%H%M%S') + '.png'
            filepath = os.path.join(OUTPUT_DIR, filename)
            with open(filepath, 'wb') as img_file:
                img_file.write(base64.b64decode(image_data.b64_json))
        elif hasattr(image_data, 'url') and image_data.url:
            image_url = image_data.url
        else:
            return jsonify({'error': '无法获取图像数据'}), 500

        return jsonify({
            'success': True,
            'image_url': image_url,
            'revised_prompt': getattr(image_data, 'revised_prompt', prompt)
        })

    except Exception as e:
        return jsonify({'error': f'生成图像时出错: {str(e)}'}), 500

if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    print("访问 http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)