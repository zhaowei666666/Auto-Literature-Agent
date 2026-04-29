"""
archive_agent.py — 归档 Agent

职责：将解析后的结构化数据格式化排版为美观的 Markdown 报告，保存到 outputs/ 目录。
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from typing import Optional

# ---------------------------------------------------------------------------
# Logging 配置（独立 Handler）
# ---------------------------------------------------------------------------
_log_format = "[Archive Agent] %(asctime)s - %(levelname)s - %(message)s"
_log_datefmt = "%Y-%m-%d %H:%M:%S"

logger = logging.getLogger("Archive Agent")
if not logger.handlers:
    _handler = logging.StreamHandler(sys.stdout)
    _handler.setFormatter(logging.Formatter(_log_format, _log_datefmt))
    logger.addHandler(_handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False


# ---------------------------------------------------------------------------
# Markdown 报告生成
# ---------------------------------------------------------------------------

def _sanitize_filename(title: str, max_len: int = 80) -> str:
    """将论文标题转为安全的文件名。"""
    # 只保留字母数字和基本标点
    safe = "".join(c if c.isalnum() or c in " _-." else " " for c in title)
    safe = " ".join(safe.split())  # 合并连续空格
    return safe[:max_len].rstrip(" .-") or "untitled"


def generate_report(
    paper_meta: dict,
    extracted_data: dict,
    pdf_path: Optional[str] = None,
    output_dir: str = "outputs",
) -> Optional[str]:
    """生成美观的 Markdown 报告并保存到 outputs/ 目录。

    Args:
        paper_meta:  论文元数据（title, authors, abstract, category, arxiv_url）。
        extracted_data: parse_agent 提取的结构化数据（innovation,
                       synthesis_conditions, performance_metrics）。
        pdf_path:    本地 PDF 文件路径（可选）。
        output_dir:  输出目录，默认 "outputs"。

    Returns:
        生成的 .md 文件路径，失败返回 None。
    """
    title = (paper_meta.get("title") or "Untitled").strip()
    safe_title = _sanitize_filename(title)
    filename = f"{safe_title}.md"
    filepath = os.path.join(output_dir, filename)

    # ---------- 组装 Markdown ----------
    md = ""

    # 标题区
    md += f"# {title}\n\n"
    md += "> 📄 **AI 自动生成报告** ·  "
    md += f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    md += "---\n\n"

    # 一、论文元数据
    authors = paper_meta.get("authors", "N/A")
    category = paper_meta.get("category", "N/A")
    arxiv_url = paper_meta.get("arxiv_url", "")
    abstract = (paper_meta.get("abstract") or "N/A").strip()

    md += "## 📋 论文元数据\n\n"
    md += "| 字段 | 内容 |\n"
    md += "|------|------|\n"
    md += f"| **标题** | {title} |\n"
    md += f"| **作者** | {authors} |\n"
    md += f"| **分类** | `{category}` |\n"
    if arxiv_url:
        arxiv_id = arxiv_url.split("/abs/")[-1] if "/abs/" in arxiv_url else arxiv_url
        md += f"| **ArXiv** | [{arxiv_id}]({arxiv_url}) |\n"
    if pdf_path:
        md += f"| **本地 PDF** | `{os.path.normpath(pdf_path)}` |\n"
    md += "\n"

    # 二、研究摘要
    md += "## 📝 研究摘要\n\n"
    md += f"{abstract}\n\n"

    # 三、AI 提取信息
    md += "## 🔬 AI 信息提取结果\n\n"

    # 3.1 核心创新点
    innovation = extracted_data.get("innovation")
    if innovation and str(innovation).strip().lower() not in ("n/a", "null", ""):
        md += "### 💡 核心创新点\n\n"
        md += f"> {innovation}\n\n"

    # 3.2 合成/制备条件
    synthesis = extracted_data.get("synthesis_conditions")
    if synthesis and str(synthesis).strip().lower() not in ("n/a", "null", ""):
        md += "### ⚗️ 合成 / 制备条件\n\n"
        md += f"{synthesis}\n\n"

    # 3.3 关键性能指标
    metrics = extracted_data.get("performance_metrics", [])
    if metrics and isinstance(metrics, list):
        md += "### 📊 关键性能指标\n\n"
        md += "| 指标 | 数值 | 单位 |\n"
        md += "|------|------|------|\n"
        for m in metrics:
            metric = (m.get("metric") or "").strip()
            value = m.get("value")
            unit = (m.get("unit") or "").strip()
            value_str = str(value) if value is not None else "—"
            md += f"| {metric} | {value_str} | {unit} |\n"
        md += "\n"

    # 原始 JSON 附件
    md += "---\n\n"
    md += "### 📎 附录：原始提取数据\n\n"
    formatted_json = json.dumps(extracted_data, ensure_ascii=False, indent=2)
    md += f"```json\n{formatted_json}\n```\n\n"

    # 页脚
    md += "---\n"
    md += f"*🕒 报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  |  "
    md += "由 AI Agent 系统自动生成*\n"

    # ---------- 写入文件 ----------
    try:
        os.makedirs(output_dir, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(md)
        logger.info("✅  Markdown 报告已生成: %s", filepath)
        return filepath
    except OSError as e:
        logger.error("❌  写入报告失败: %s", str(e))
        return None


# ---------------------------------------------------------------------------
# CLI 入口（独立使用时）
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Archive Agent — 结构化数据 → Markdown 报告",
    )
    parser.add_argument("--input", "-i", type=str, required=True,
                        help="parse_agent 输出的 JSON 文件路径")
    parser.add_argument("--output-dir", "-o", type=str, default="outputs",
                        help="报告输出目录（默认: outputs）")
    parser.add_argument("--pdf-path", type=str, default=None,
                        help="PDF 文件路径（可选）")
    args = parser.parse_args()

    try:
        with open(args.input, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error("❌  读取 JSON 失败: %s", str(e))
        sys.exit(1)

    # 兼容单篇 / 批量结果
    if isinstance(data, list):
        for item in data:
            if "error" in item:
                logger.warning("⚠️  跳过 %s: %s", item.get("file", "unknown"), item["error"])
                continue
            meta = _extract_meta_from_item(item)
            generate_report(meta, item, pdf_path=args.pdf_path, output_dir=args.output_dir)
    else:
        if "error" in data:
            logger.error("❌  数据中包含错误: %s", data["error"])
            sys.exit(1)
        generate_report(data, data, pdf_path=args.pdf_path, output_dir=args.output_dir)

    logger.info("🎉  All done!")


def _extract_meta_from_item(item: dict) -> dict:
    """从 parse_agent 输出的 item 中提取元数据（缺失字段使用占位符）。"""
    title = item.get("file", "Untitled")
    # 尝试从文件名反推标题：移除 arXiv ID 前缀和扩展名
    if title.endswith(".pdf"):
        title = title[:-4]
    # 移除 arXiv ID 前缀，如 "2604.12345v1."
    parts = title.split(".", 2)
    if len(parts) >= 3 and parts[0].isdigit() and len(parts[0]) == 4:
        title = parts[2].replace("_", " ")
    title = title.strip() or "Unknown Paper"
    return {
        "title": title,
        "authors": item.get("authors", "N/A"),
        "abstract": item.get("abstract", "N/A"),
        "category": item.get("category", "N/A"),
        "arxiv_url": item.get("arxiv_url", ""),
    }


if __name__ == "__main__":
    main()
