<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat&logo=python&logoColor=white" alt="Python 3.10+"/>
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg?style=flat" alt="MIT License"/>
  <img src="https://img.shields.io/badge/ArXiv-API-red.svg?style=flat&logo=arxiv" alt="ArXiv API"/>
  <img src="https://img.shields.io/badge/LLM-OpenAI%20Compatible-blueviolet.svg?style=flat" alt="LLM Compatible"/>
  <img src="https://img.shields.io/badge/Docker-Ready-2496ED.svg?style=flat&logo=docker" alt="Docker Ready"/>
</p>

<h1 align="center">
  🔬 Auto-Literature-Agent
</h1>

<p align="center">
  <b>多 Agent 协作式学术文献自动化深度解析系统</b><br>
  <i>Search → Parse → Archive — 从检索到结构化数据，全流程闭环</i>
</p>

<p align="center">
  <a href="#-quick-demo">快速上手</a> ·
  <a href="#-architecture">架构</a> ·
  <a href="#-installation">安装</a> ·
  <a href="#%EF%B8%8F-configuration">配置</a> ·
  <a href="#-usage">使用指南</a>
</p>

---

## 📌 Quick Demo

```bash
# 1️⃣  一键安装
pip install -r requirements.txt

# 2️⃣  配置 API（.env 或环境变量）
echo 'LLM_API_KEY=sk-your-key' >> .env
echo 'LLM_BASE_URL=https://api.deepseek.com/v1' >> .env
echo 'LLM_MODEL_NAME=deepseek-chat' >> .env

# 3️⃣  跑起来
python main.py --query "solid-state battery electrolytes"
```

终端输出预览：

```
╔══════════════════════════════════════════════════════════════╗
║       🔬  AI Academic Literature & Data Parsing Agent      ║
╚══════════════════════════════════════════════════════════════╝

[Agent Orchestrator]  收到指令，开始分解任务...
  └─ ▶ 阶段 1/3: 论文检索与下载  [Search Agent]
[Search Agent]        🔍 Searching ArXiv...
[Search Agent]        ✅ Found 1 paper(s)
[Search Agent]        ⬇ Downloading PDF...
  └─ ▶ 阶段 2/3: 长文本信息抽取  [Parse Agent]
[Parse Agent]         📖 Reading PDF...
[Parse Agent]         🤖 Calling LLM...
  └─ ▶ 阶段 3/3: 生成最终报告  [Archive Agent]
[Archive Agent]       ✅ Markdown 报告已生成: outputs/xxx.md

🎉  全流程完成！ 📄 报告 → outputs/  📎 PDF → pdfs/
```

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      main.py                                │
│                 Agent Orchestrator                          │
│         调度链: Search → Parse → Archive                    │
└─────────────────────────────────────────────────────────────┘
        │                │                │
        ▼                ▼                ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Search Agent │ │  Parse Agent │ │Archive Agent │
├──────────────┤ ├──────────────┤ ├──────────────┤
│ • ArXiv API  │ │ • PDF读取    │ │ • Markdown   │
│ • 元数据提取  │ │ • 文本清洗   │ │ • 结构化排版  │
│ • PDF 下载   │ │ • LLM 精读  │ │ • 参数表格化  │
│              │ │ • JSON 解析  │ │              │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │
       ▼                ▼                ▼
   📎 pdfs/         🤖 LLM API        📄 outputs/
```

| 模块 | 职责 | 关键技术 |
|------|------|----------|
| 🔍 **Search Agent** | 接收关键词 → 检索 ArXiv → 下载 PDF | `arxiv` SDK, `requests` |
| 📖 **Parse Agent** | 读取 PDF → LLM 提取结构化参数 → 输出 JSON | `pdfplumber`, `openai` SDK, 文本清洗 |
| 📝 **Archive Agent** | 结构化 JSON → 美观 Markdown 数据报告 | Markdown 模板引擎 |

---

## ✨ Features

<table>
<tr>
  <td width="50%">
    <h3>🤖 多 Agent 协作</h3>
    <p>三个独立 Agent 串行协作，各司其职。终端实时打印带 Agent 前缀的日志流，像看团队协作一样清晰。</p>
  </td>
  <td width="50%">
    <h3>🧠 LLM 深度解析</h3>
    <p>不止是摘要提取。针对材料科学场景定制 Prompt，提取核心创新点、合成条件、性能指标（含数值+单位）。</p>
  </td>
</tr>
<tr>
  <td width="50%">
    <h3>🔌 任意 LLM 兼容</h3>
    <p>OpenAI 兼容接口均可接入 — DeepSeek、通义千问、GLM、Claude、本地 vLLM 等。仅需配置 <code>BASE_URL</code> + <code>API_KEY</code>。</p>
  </td>
  <td width="50%">
    <h3>📊 结构化数据报告</h3>
    <p>输出为精美的 Markdown 文件：元数据表 → 研究摘要 → 创新点 → 合成条件 → 性能指标表格 → 原始 JSON 附录。可直接归档或分享。</p>
  </td>
</tr>
<tr>
  <td width="50%">
    <h3>🐳 Docker 可部署</h3>
    <p>提供生产级 Dockerfile，一行命令构建镜像，适合服务器/集群批量运行。</p>
  </td>
  <td width="50%">
    <h3>📦 轻量零依赖框架</h3>
    <p>纯 Python 实现，不依赖 LangChain 等重型框架。核心依赖仅 4 个包，易于二次开发和定制。</p>
  </td>
</tr>
</table>

---

## 🛠 Installation

### 环境要求

- Python 3.10+
- pip

### 步骤

```bash
# 1. 克隆仓库
git clone https://github.com/zhaowei666666/Auto-Literature-Agent.git
cd Auto-Literature-Agent

# 2. 安装依赖（4 个轻量包）
pip install -r requirements.txt

# 3. 配置 API（二选一）
# 方式 A：使用 .env 文件（推荐）
cp .env.example .env
# 编辑 .env 填入你的 API Key ...

# 方式 B：使用环境变量
# Windows (PowerShell)
$env:LLM_API_KEY="sk-your-key"
$env:LLM_BASE_URL="https://api.deepseek.com/v1"
$env:LLM_MODEL_NAME="deepseek-chat"

# Linux / macOS
export LLM_API_KEY="sk-your-key"
export LLM_BASE_URL="https://api.deepseek.com/v1"
export LLM_MODEL_NAME="deepseek-chat"
```

---

## ⚙️ Configuration

### 环境变量

| 变量 | 说明 | 是否必填 | 示例 |
|------|------|----------|------|
| `LLM_API_KEY` | 大模型 API 密钥 | ✅ 是 | `sk-xxxx....` |
| `LLM_BASE_URL` | API 基础地址（须以 `/v1` 结尾） | ✅ 是 | `https://api.deepseek.com/v1` |
| `LLM_MODEL_NAME` | 模型名称 | ✅ 是 | `deepseek-chat` / `gpt-4o` / `qwen-plus` |

### 支持的模型服务商

| 服务商 | `BASE_URL` 示例 | `MODEL_NAME` 示例 |
|--------|-----------------|-------------------|
| **DeepSeek** | `https://api.deepseek.com/v1` | `deepseek-chat` |
| **OpenAI** | `https://api.openai.com/v1` | `gpt-4o`, `gpt-4-turbo` |
| **通义千问** | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `qwen-plus`, `qwen-max` |
| **智谱 GLM** | `https://open.bigmodel.cn/api/paas/v4` | `glm-4-plus` |
| **Anthropic** | `https://api.anthropic.com` | `claude-sonnet-4-20250514` |
| **本地 vLLM** | `http://localhost:8000/v1` | `your-model-name` |

---

## 📖 Usage

### 基本用法

```bash
# 单次搜索 → 解析 → 归档
python main.py --query "photocatalytic materials water treatment"
```

### 批量搜索示例

```bash
python main.py --query "solid-state battery electrolytes"
python main.py --query "2D materials gas sensing"
python main.py --query "high entropy alloys"
python main.py --query "perovskite solar cells stability"
```

### 可选参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--max-chars` | `12000` | 传给 LLM 的最大文本量（字符数） |
| `--output-dir` | `outputs` | Markdown 报告输出目录 |
| `--pdf-dir` | `pdfs` | PDF 缓存目录 |

### 各 Agent 独立使用

```bash
# 仅检索下载
python search_agent.py --query "quantum computing" -n 3

# 仅解析已有 PDF
python parse_agent.py --dir pdfs/

# 仅从 JSON 生成报告
python archive_agent.py -i results.json
```

---

## 📂 Project Structure

```
Auto-Literature-Agent/
├── main.py              # 🎯 Agent Orchestrator — 统一调度入口
├── search_agent.py      # 🔍 Search Agent — ArXiv 检索 + PDF 下载
├── parse_agent.py       # 📖  Parse Agent  — PDF 读取 + LLM 精读 + JSON 输出
├── archive_agent.py     # 📝  Archive Agent — Markdown 报告生成
├── requirements.txt     # 📦 依赖清单（共 4 个包）
├── .env.example         # 🔑 环境变量模板
├── Dockerfile           # 🐳 Docker 构建文件
├── pdfs/                # 📎 PDF 存储目录
├── outputs/             # 📄 Markdown 报告输出目录
├── .gitignore
├── LICENSE              # MIT 协议
└── README.md
```

---

## 📄 License

[MIT](LICENSE)

---

<p align="center">
  <sub>Built with ❤️ for the research community · 自动解析，赋能科研</sub>
</p>
