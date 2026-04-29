# Frontier Literature & Core Data Automated Analysis Agent (Auto-Literature-Agent)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

## 🚀 项目简介

**Auto-Literature-Agent** 是一款专为**前沿材料科学、化学工程及环境工程**等领域设计的学术文献自动化深度解析工具。该系统基于多 Agent 协作架构，能够自动完成“检索 -> 下载 -> 信息抽取 -> 数据结构化 -> Markdown 报告生成”的全流程闭环。

在当前科技爆发的背景下，科研人员面临海量文献阅读压力。本项目旨在利用大语言模型（LLM）的深度语义理解能力，从海量 PDF 文献中精准提取**实验参数、性能指标（如电导率、光催化效率、稳定性等）、核心创新点以及材料配方**，极大提升科研情报调研效率。

## ✨ 核心特性

-   **多 Agent 协同工作流**：
    -   🔍 **Search Agent**：精准检索 ArXiv 等学术数据库，自动匹配关键词并完成 PDF 异步下载。
    -   📖 **Parse Agent**：基于 `pdfplumber` 结合 LLM，跨越 PDF 格式障碍，深度解析长文本内容。
    -   📝 **Archive Agent**：将抽取的零散数据重组为结构化的专业学术快报。
-   **业务场景深耕**：预设了针对材料科学（如 OECTs 打印电解质、固态电池）、环境工程（光催化、水处理）的解析 Prompt。
-   **高度可扩展**：支持自定义 LLM 配置，完美适配国内外主流 API 接口及本地私有化模型。

## 🛠️ 安装说明

### 环境依赖
-   Python 3.10+
-   已安装 [git](https://git-scm.com/)

### 步骤
1.  **克隆仓库**
    ```bash
    git clone https://github.com/your-username/Auto-Literature-Agent.git
    cd Auto-Literature-Agent
    ```

2.  **安装依赖**
    ```bash
    pip install -r requirements.txt
    ```

## ⚙️ 配置说明 (重要)

本项目使用环境变量进行 LLM 配置。为了支持不同的模型供应商（如 OpenAI, Anthropic, DeepSeek, OneAPI 等），请在运行前配置以下环境变量：

### 环境变量配置

| 变量名 | 说明 | 示例 |
| :--- | :--- | :--- |
| `LLM_API_KEY` | 您的 API 密钥 | `sk-xxxx....` |
| `LLM_BASE_URL` | API 的基础路径 (支持自定义特殊路径) | `https://api.openai.com/v1` 或 `https://your-proxy.com/v1` |
| `LLM_MODEL_NAME` | 调用的模型名称 | `gpt-4-turbo`, `claude-3-opus`, `deepseek-chat` |

#### 配置示例 (Windows PowerShell):
```powershell
$env:LLM_API_KEY="sk-your-key-here"
$env:LLM_BASE_URL="https://api.example.com/v1"
$env:LLM_MODEL_NAME="gpt-4o"
```

#### 配置示例 (Linux/macOS):
```bash
export LLM_API_KEY="sk-your-key-here"
export LLM_BASE_URL="https://api.example.com/v1"
export LLM_MODEL_NAME="gpt-4o"
```

## 📖 使用指南

直接运行 `main.py` 并提供搜索关键词：

```bash
python main.py --query "biocompatible printed electrolytes for OECTs"
```

### 可选参数：
-   `--max-chars`: 传给 LLM 的最大文本量（默认 12000）。
-   `--output-dir`: 报告保存目录（默认 `outputs/`）。
-   `--pdf-dir`: PDF 缓存目录（默认 `pdfs/`）。

## 📂 项目结构
```text
.
├── main.py             # Agent 协同调度中心
├── search_agent.py      # 文献检索与下载模块
├── parse_agent.py       # PDF 解析与信息抽取模块
├── archive_agent.py     # 报告生成与归档模块
├── requirements.txt     # 项目依赖
├── pdfs/               # PDF 存储目录 (已忽略)
└── outputs/            # Markdown 报告输出目录 (已忽略)
```

## 📄 开源协议
本项目基于 [MIT License](LICENSE) 协议开源。
