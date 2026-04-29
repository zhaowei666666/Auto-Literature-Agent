"""
main.py — Agent Orchestrator

职责：统一调度 Search Agent → Parse Agent → Archive Agent，完成自动化闭环。
终端呈现多 Agent 协作式日志流。
"""

import argparse
import logging
import os
import sys

import search_agent
import parse_agent
import archive_agent

# ---------------------------------------------------------------------------
# Logging 配置（独立 Handler）
# ---------------------------------------------------------------------------
_log_format = "[Agent Orchestrator] %(asctime)s - %(levelname)s - %(message)s"
_log_datefmt = "%Y-%m-%d %H:%M:%S"

logger = logging.getLogger("Agent Orchestrator")
if not logger.handlers:
    _handler = logging.StreamHandler(sys.stdout)
    _handler.setFormatter(logging.Formatter(_log_format, _log_datefmt))
    logger.addHandler(_handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False


# ---------------------------------------------------------------------------
# Banner
# ---------------------------------------------------------------------------
BANNER = r"""
╔══════════════════════════════════════════════════════════════╗
║       🔬  AI Academic Literature & Data Parsing Agent      ║
║       多 Agent 协作式学术文献与核心数据自动化解析系统       ║
╚══════════════════════════════════════════════════════════════╝
"""


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

def run_pipeline(
    query: str,
    max_chars: int = 12000,
    output_dir: str = "outputs",
    pdf_dir: str = "pdfs",
) -> str | None:
    """执行完整解析管线。

    流程: 检索 → 元数据提取 → PDF 下载 → LLM 解析 → Markdown 归档。

    Args:
        query:      学术关键词。
        max_chars:  传给 LLM 的最大字符数。
        output_dir: Markdown 报告输出目录。
        pdf_dir:    PDF 下载目录。

    Returns:
        最终 Markdown 报告路径，失败则返回 None。
    """
    logger.info("=" * 59)
    logger.info("  收到指令，开始分解任务...")
    logger.info("  用户请求: \"%s\"", query)
    logger.info("  调度链: Search → Parse → Archive")
    logger.info("=" * 59)

    # ------------------------------------------------------------------
    # 阶段 1 — Search Agent
    # ------------------------------------------------------------------
    logger.info("")
    logger.info("─" * 59)
    logger.info("  ▶ 阶段 1/3: 论文检索与下载  [Search Agent]")
    logger.info("─" * 59)

    papers = search_agent.search_papers(query, max_results=1)
    if not papers:
        logger.error("[Search Agent] ❌ 未找到匹配论文，终止流程")
        return None
    paper = papers[0]

    title = paper.title.replace("\n", " ").strip()
    authors = ", ".join(a.name for a in paper.authors)
    logger.info("[Search Agent] 📄  命中论文: \"%s\"", title)
    logger.info("[Search Agent] 👥  作者: %s", authors)
    logger.info("[Search Agent] 📂  分类: %s", paper.primary_category)
    logger.info("[Search Agent] 🔗  ArXiv: %s", paper.entry_id)

    pdf_path = search_agent.download_pdf(paper, output_dir=pdf_dir)
    if not pdf_path:
        logger.error("[Search Agent] ❌ PDF 下载失败，终止流程")
        return None
    logger.info("[Search Agent] ✅  PDF 下载完成")

    # ------------------------------------------------------------------
    # 阶段 2 — Parse Agent
    # ------------------------------------------------------------------
    logger.info("")
    logger.info("─" * 59)
    logger.info("  ▶ 阶段 2/3: 长文本信息抽取  [Parse Agent]")
    logger.info("─" * 59)

    logger.info("[Parse Agent] 📖  正在读取 PDF: %s", os.path.basename(pdf_path))
    extracted = parse_agent.extract_paper_info(pdf_path, max_chars=max_chars)

    if "error" in extracted and extracted["error"]:
        logger.error("[Parse Agent] ❌ 解析失败: %s", extracted["error"])
        return None

    logger.info("[Parse Agent] ✅  信息抽取完成")
    innovation = extracted.get("innovation", "")
    if innovation:
        logger.info("[Parse Agent] 💡  核心创新: %s", str(innovation)[:120].replace("\n", " "))

    metrics = extracted.get("performance_metrics", [])
    if metrics:
        logger.info("[Parse Agent] 📊  提取 %d 项性能指标", len(metrics))

    # ------------------------------------------------------------------
    # 阶段 3 — Archive Agent
    # ------------------------------------------------------------------
    logger.info("")
    logger.info("─" * 59)
    logger.info("  ▶ 阶段 3/3: 生成最终报告  [Archive Agent]")
    logger.info("─" * 59)

    logger.info("[Archive Agent] 📝  数据已结构化，正在生成最终报告...")

    paper_meta = {
        "title": title,
        "authors": authors,
        "abstract": paper.summary.replace("\n", " ").strip(),
        "category": paper.primary_category,
        "arxiv_url": paper.entry_id,
    }

    report_path = archive_agent.generate_report(
        paper_meta=paper_meta,
        extracted_data=extracted,
        pdf_path=pdf_path,
        output_dir=output_dir,
    )

    if not report_path:
        logger.error("[Archive Agent] ❌ 报告生成失败")
        return None

    # ------------------------------------------------------------------
    # 完成
    # ------------------------------------------------------------------
    logger.info("")
    logger.info("=" * 59)
    logger.info("  🎉  全流程完成！")
    logger.info("=" * 59)
    logger.info("  📄  报告: %s", report_path)
    logger.info("  📎  PDF:  %s", pdf_path)
    logger.info("=" * 59)

    # 打印报告预览路径
    print(f"\n📄 Markdown 报告已保存至: {os.path.abspath(report_path)}\n")

    return report_path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    print(BANNER)

    parser = argparse.ArgumentParser(
        description="AI Academic Literature & Data Parsing Agent — 多 Agent 协作式论文解析系统",
    )
    parser.add_argument(
        "-q", "--query",
        type=str,
        required=True,
        help='学术关键词，例如 "新型光催化降解材料" 或 "solid-state battery electrolytes"',
    )
    parser.add_argument(
        "--max-chars",
        type=int,
        default=12000,
        help="LLM 输入最大字符数（默认: 12000）",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="outputs",
        help="Markdown 报告输出目录（默认: outputs）",
    )
    parser.add_argument(
        "--pdf-dir",
        type=str,
        default="pdfs",
        help="PDF 下载目录（默认: pdfs）",
    )
    args = parser.parse_args()

    # 检查 LLM 环境变量是否配置
    required_envs = ["LLM_API_KEY", "LLM_BASE_URL", "LLM_MODEL_NAME"]
    missing_envs = [v for v in required_envs if not os.environ.get(v)]
    if missing_envs:
        logger.warning(
            "⚠️  检测到 LLM 环境变量未完全配置: %s\n"
            "    Parse Agent 阶段将因缺少 API 凭据而失败。\n"
            "    请设置:\n"
            "      set LLM_API_KEY=sk-your-key\n"
            "      set LLM_BASE_URL=https://api.example.com/v1\n"
            "      set LLM_MODEL_NAME=your-model",
            ", ".join(missing_envs),
        )
        logger.warning("继续执行，但 Parse Agent 阶段将跳过 LLM 调用。")

    run_pipeline(
        query=args.query,
        max_chars=args.max_chars,
        output_dir=args.output_dir,
        pdf_dir=args.pdf_dir,
    )


if __name__ == "__main__":
    main()
