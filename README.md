# Image-2 Generator

> 基于 OpenAI gpt-image-2 API 的图像生成与编辑工具，内建 mask 绘制功能，支持失败自动重试。

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/flask-2.3%2B-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

---

## ✨ 功能

| 功能 | 说明 |
|------|------|
| 🖼️ **生图模式** | 上传多张参考图，一次性全部提交给 API |
| 🎨 **改图模式** | 上传 1 张参考图 + 在浏览器内绘制 mask 遮罩，指定编辑区域 |
| 🔄 **失败重试** | API 调用失败自动重试，最多 10 次，UI 实时显示每次错误 |
| 💾 **本地保存** | 生成的图片自动保存到 `outputs/` 目录 |
| 📱 **响应式 UI** | 暗色主题，支持拖拽上传、键盘 Enter 快捷提交 |

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API

复制 `.env` 并填入你的 API 密钥：

```env
OPENAI_API_KEY=sk-your-key-here
OPENAI_BASE_URL=https://api.rua.chat/v1
```

> `OPENAI_BASE_URL` 使用 rua.chat 代理，也可以换成官方 `https://api.openai.com/v1`。

### 3. 启动服务

```bash
# 方式一
python run.py

# 方式二
python app.py
```

访问 http://localhost:5000 即可使用。

---

## 📁 项目结构

```
image-2-generator/
├── app.py                 # Flask 后端（API 路由 + OpenAI 调用）
├── run.py                 # 启动入口
├── requirements.txt       # Python 依赖
├── .env                   # 环境变量（API 密钥）
├── README.md              # 项目说明
├── ARCHITECTURE.md        # 架构文档
├── CHANGELOG.md           # 版本日志
├── templates/
│   └── index.html         # 前端单页应用
├── static/                # 静态资源（预留）
├── outputs/               # 生成的图片保存目录
└── docs/                  # 详细文档
    ├── api.md             # API 参考
    ├── mask-guide.md      # Mask 绘制指南
    └── troubleshooting.md # 故障排查
```

---

## 🎨 使用说明

### 生图模式（默认）

1. 选择 **🖼️ 生图模式**
2. 上传 1~多张参考图
3. 填写图像描述
4. 点击 **生成图像**

> 参考图用于引导风格/构图，API 以 `images.edit` 多图模式提交。

### 改图模式

1. 选择 **🎨 改图模式**
2. 上传 1 张参考图 → 自动弹出画布
3. 在图上**涂白色** = 要修改的区域；**透明** = 保留原样
4. 可调整笔刷大小（3~80px）、切换橡皮、一键清除
5. 填写修改描述
6. 点击 **生成图像**

> **Mask 规则**：白色区域 = API 将在此区域应用修改，透明区域 = 完全保留原图内容。

---

## ⚙️ 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Flask 2.3 + OpenAI SDK 2.x |
| 前端 | 原生 HTML5 + CSS3 + ES6 JavaScript |
| API | OpenAI gpt-image-2（images.generate / images.edit） |
| 画布 | HTML5 Canvas 2D API |

---

## 📝 环境变量

| 变量 | 必填 | 说明 |
|------|------|------|
| `OPENAI_API_KEY` | ✅ | API 密钥 |
| `OPENAI_BASE_URL` | ❌ | API 地址，默认 `https://api.rua.chat/v1` |

---

## ⚠️ 注意事项

- 图片上传限制：50MB（`app.config['MAX_CONTENT_LENGTH']`）
- 参考图格式：PNG / JPG / JPEG / WEBP / GIF
- Mask 图：Canvas 自动导出为透明 PNG
- 改图模式下 API 只使用第 1 张参考图
- 生图模式支持多图，最多 10 张

---

## 📄 许可证

MIT
