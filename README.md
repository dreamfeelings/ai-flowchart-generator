# 🎨 AI图表生成器

一个基于Flask和AI的自动图表生成网站，使用自然语言描述即可生成专业美观的流程图和ER图。

## ✨ 功能特点

- 🤖 **AI驱动** - 使用GPT-4o模型理解自然语言并生成图表
- 🎯 **简单易用** - 无需学习复杂语法，用自然语言描述即可
- 🎨 **多种主题** - 支持6种精美主题（简约灰色、清新多彩、优雅暗色、自然森林、极简黑白、经典蓝调）
- 📊 **四种图表** - 支持流程图、现代ER图、陈氏ER图、思维导图
- 🎭 **智能样式** - 自动为节点添加颜色标记（成功/失败/警告/信息）
- 💾 **导出功能** - 支持导出SVG和PNG格式
- 📱 **响应式设计** - 完美支持移动端和桌面端
- ⚡ **快速示例** - 内置多个示例，快速上手
- 📚 **符号说明** - ER图关系符号详细说明

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置API

复制配置文件模板并填入你的API密钥：

```bash
# Windows
copy config.example.py config.py

# Linux/Mac
cp config.example.py config.py
```

然后编辑 `config.py`，填入你的真实配置：

```python
API_BASE_URL = "https://api.example.com"
API_KEY = "your-api-key-here"
MODEL = "gpt-4o"
```

### 3. 运行应用

```bash
python app.py
```

访问 http://localhost:5000 即可使用。

## ⚠️ 安全提示

- `config.py` 包含敏感信息，已添加到 `.gitignore`
- 请勿将 `config.py` 提交到版本控制系统
- 使用 `config.example.py` 作为配置模板

### 使用方法

1. 在左侧文本框输入流程描述（中文或英文）
2. 点击"生成流程图"按钮
3. 等待AI生成流程图
4. 可以下载为SVG或PNG格式

## 📋 示例描述

- "创建一个用户登录流程，包含输入用户名密码、验证、登录成功或失败的处理"
- "设计一个电商订单处理流程，从下单到配送完成"
- "展示敏捷开发的完整流程，包括需求分析、设计、开发、测试、部署"
- "员工请假审批系统的流程图，包含申请、主管审批、HR审批等环节"

## 🔧 技术栈

### 后端
- **Flask** - Web框架
- **Requests** - HTTP客户端
- **OpenAI API** - AI接口（GPT-4o）

### 前端
- **HTML5/CSS3** - 页面结构和样式
- **JavaScript** - 交互逻辑
- **Mermaid.js** - 流程图渲染引擎

## 📁 项目结构

```
流程图生成/
├── app.py                 # Flask主应用
├── templates/
│   └── index.html        # 前端页面
├── requirements.txt      # Python依赖
└── README.md            # 项目文档
```

## ⚙️ 配置说明

在 `app.py` 中配置AI接口：

```python
API_BASE_URL = "https://api.ephone.ai"
API_KEY = "your-api-key"
MODEL = "gpt-4o"
```

## 🎯 核心功能

### 1. AI流程图生成
- 调用GPT-4o模型
- 智能理解自然语言描述
- 生成标准Mermaid语法代码

### 2. 实时渲染
- 使用Mermaid.js实时渲染
- 支持多种流程图样式
- 自动优化布局

### 3. 导出功能
- **SVG格式** - 矢量图，可无损缩放
- **PNG格式** - 位图，便于分享

### 4. 响应式界面
- 美观的渐变背景
- 流畅的动画效果
- 移动端适配

## 🌟 使用技巧

1. **描述要清晰** - 包含主要步骤和流程分支
2. **使用中文** - AI对中文理解很好
3. **Ctrl+Enter** - 快捷键生成流程图
4. **参考示例** - 点击示例快速开始

## 📝 API接口

### POST /generate
生成流程图

**请求体：**
```json
{
  "description": "流程描述"
}
```

**响应：**
```json
{
  "success": true,
  "mermaid_code": "flowchart TD\n  A[开始] --> B[结束]"
}
```

### GET /examples
获取示例列表

**响应：**
```json
[
  {
    "title": "示例标题",
    "description": "示例描述"
  }
]
```

## 🔒 安全说明

- API密钥已内置在代码中，生产环境建议使用环境变量
- 建议添加请求频率限制
- 生产环境建议添加用户认证

## 📈 扩展建议

- [ ] 添加用户系统和历史记录
- [ ] 支持更多图表类型（时序图、甘特图等）
- [ ] 添加在线编辑功能
- [ ] 集成更多AI模型
- [ ] 添加协作功能

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## 👨‍💻 作者

AI流程图生成器项目

---

**Enjoy creating beautiful flowcharts with AI! 🎉**
