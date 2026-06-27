# Architecture

> Image-2 Generator — 架构设计文档

---

## 1. 系统概览

```
┌─────────────────────────────────────────────────────┐
│                    Browser (Frontend)                │
│  ┌─────────┐ ┌─────────┐ ┌──────────────────────┐  │
│  │ 参考图   │ │ Mask    │ │   生成控制台          │  │
│  │ 上传区   │ │ 画布区  │ │  (prompt+按钮)        │  │
│  └────┬────┘ └────┬────┘ └──────────┬───────────┘  │
│       │          │                  │              │
│       └──────────┴──────────────────┘              │
│              FormData (POST /generate)              │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│                  Flask (Backend)                     │
│  ┌────────────────────────────────────────────────┐ │
│  │  GET  /          →  index.html                  │ │
│  │  POST /generate  →  generate_image()            │ │
│  └────────────────────┬───────────────────────────┘ │
│                       │                              │
│              ┌────────▼────────┐                     │
│              │  Mode Router     │                    │
│              │  mode=generate  │→ images.edit (多图)  │
│              │  mode=edit      │→ images.edit (单图)  │
│              │  no image       │→ images.generate    │
│              └────────┬─────────┘                    │
└───────────────────────┼──────────────────────────────┘
                        │
┌───────────────────────▼──────────────────────────────┐
│              OpenAI API (gpt-image-2)                 │
│   POST /images/generate  POST /images/edit           │
└───────────────────────────────────────────────────────┘
```

---

## 2. 后端架构

### 2.1 路由

| 路由 | 方法 | 功能 |
|------|------|------|
| `/` | GET | 返回前端页面 |
| `/generate` | POST | 接收 prompt + images + mask + mode，返回生成结果 |

### 2.2 核心逻辑

```python
# generate_image() 处理流程
1. 解析 prompt
2. 获取文件列表 (images) + mask + mode
3. 根据 mode 路由：
   - mode=generate → images.edit(多图)
   - mode=edit     → images.edit(单图 + mask)
   - 无图           → images.generate(纯文本)
4. 解析 API 返回
5. 保存到 outputs/ 并返回 base64
```

### 2.3 数据流

```
FormData
  ├── prompt (str)
  ├── mode   (str: 'generate' | 'edit')
  ├── images (file list)
  └── mask   (file, optional, PNG blob)
         │
         ▼
   generate_image()
         │
         ├── mode='generate'
         │     └── client.images.edit(image=[tuple, ...])
         │
         ├── mode='edit'
         │     └── client.images.edit(image=tuple, mask=tuple)
         │
         └── no images
               └── client.images.generate(prompt=prompt)
```

---

## 3. 前端架构

### 3.1 模块划分

```
index.html
├── Style
│   ├── 全局主题 (暗色 + 紫色调)
│   ├── 模式选择器 (.mode-selector)
│   ├── 上传区 (.upload-zone)
│   ├── 画布绘制区 (.draw-container)
│   ├── 结果/重试区 (.retry-status)
│   └── 工具类 (.error / .success / .loading)
│
├── DOM 结构
│   ├── 模式切换按钮
│   ├── 参考图上传区 + 预览网格
│   ├── mask 画布区（改图模式显示）
│   ├── prompt 输入框
│   ├── 生成按钮
│   ├── 重试状态面板
│   └── 结果显示区
│
└── Script
    ├── 上传管理 (selectedFiles[])
    ├── 模式切换 (switchMode)
    ├── 画布绘制 (Canvas 2D)
    ├── 生成调用 (generateImage + 重试循环)
    └── 工具函数 (showError / showSuccess / renderRetryErrors)
```

### 3.2 状态机

```
idle ──选图──▶ selecting ──切模式──▶ mode_switch
                          │
                    ┌─────┴──────┐
                    ▼             ▼
              generate_mode    edit_mode
              (多图上传)       (单图+画布)
                    │             │
                    └──────┬──────┘
                           ▼
                      generating
                    (重试循环 ≤10次)
                           │
              ┌────────────┼────────────┐
              ▼                         ▼
           success                    fail
           (显示图片)              (显示错误列表)
```

### 3.3 Canvas Mask 机制

```
用户画白色 ──► canvas 2D stroke (source-over, #FFFFFF)
用户擦除  ──► canvas 2D stroke (destination-out)
生成时    ──► canvas.toBlob('image/png')
           ──► FormData.append('mask', blob, 'mask.png')
           ──► POST /generate
```

关键坐标映射：
```javascript
canvasX = (e.clientX - rect.left) * (canvas.width / rect.width)
canvasY = (e.clientY - rect.top)  * (canvas.height / rect.height)
// canvas.width = 图片 naturalWidth（原始分辨率）
```

### 3.4 重试机制

```javascript
for (attempt = 1; attempt <= MAX_RETRIES(10); attempt++) {
    data = fetch('/generate')
    if (data.success === true)  break  // 成功退出
    errors.push(attempt, data.error)   // 失败记录
}
// 全部失败 → 显示10条错误日志
```

---

## 4. 关键设计决策

| 决策 | 原因 |
|------|------|
| 前端重试而非后端 | 保持后端 stateless，重试状态由 UI 实时反馈 |
| Canvas 原始分辨率导出 | Mask 精度和参考图一致，避免缩放失真 |
| 改图模式强制 1 张图 | OpenAI edit API 只支持 1 image + 1 mask |
| mode 参数路由 | 单一路口复用，减少 Flask 路由数量 |
| .env 而非 config.py | 简单项目不引入配置层，dotenv 足够 |

---

## 5. 依赖关系

```
app.py
  ├── flask          ← Web 框架
  ├── openai         ← OpenAI SDK（调用 gpt-image-2）
  └── python-dotenv  ← 加载 .env

index.html
  └── 无外部依赖     ← 纯原生 HTML/CSS/JS
```

---

## 6. 安全考虑

- API Key 硬编码在 `.env`，`app.py` 通过 `load_dotenv()` 加载，不提交到 git
- `.env` 在 `.gitignore` 中（应配置）
- `MAX_CONTENT_LENGTH` 限制上传大小防止滥用
- 所有错误走统一 `except`，不暴露堆栈给前端
