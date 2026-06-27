#!/usr/bin/env python3
"""
Image-2 图像生成器启动脚本
"""

import subprocess
import sys
import os

def main():
    # 检查是否安装了依赖
    try:
        import flask
        import openai
        import dotenv
    except ImportError as e:
        print(f"缺少必要的依赖: {e}")
        print("正在安装依赖...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # 检查 .env 文件是否存在
    if not os.path.exists('.env'):
        print("警告: 未找到 .env 文件，将使用默认 API 密钥")
    
    # 启动 Flask 应用
    print("启动 Image-2 图像生成器...")
    print("请访问 http://localhost:5000 查看界面")
    print("按 Ctrl+C 停止服务器")
    
    from app import app
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()