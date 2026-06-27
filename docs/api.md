# API 参考

## POST /generate

生成或编辑图像。

### 请求

**Content-Type**: `multipart/form-data`

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `prompt` | string | ✅ | 图像描述 |
| `mode` | string | ❌ | `generate` 生图模式 / `edit` 改图模式（默认 `edit`） |
| `images` | file[] | ❌ | 参考图片（1~多张） |
| `mask` | file | ❌ | 遮罩图片（改图模式可用，PNG 透明） |

### 响应

**成功 (200)**

```json
{
    "success": true,
    "image_url": "data:image/png;base64,{...}",
    "revised_prompt": "优化后的提示词"
}
```

**失败 (400/500)**

```json
{
    "error": "错误描述"
}
```

---

## 路由表

| 路由 | 方法 | 功能 |
|------|------|------|
| `/` | GET | 返回前端页面 |
| `/generate` | POST | 图像生成/编辑 |

---

## 依赖环境变量

| 变量 | 说明 |
|------|------|
| `OPENAI_API_KEY` | OpenAI API 密钥 |
| `OPENAI_BASE_URL` | API Base URL（默认 rua.chat 代理） |
