"""
search_agent.py — 检索 Agent

职责：接收学术关键词 → 调用 ArXiv API → 获取最新论文元数据 → 下载 PDF 到本地
"""

import argparse
import logging
import os
import sys
from typing import List, Optional

import arxiv

# ---------------------------------------------------------------------------
# Logging 配置（独立 Handler，避免被主调度器重复配置）
# ---------------------------------------------------------------------------
_log_format = "[Search Agent] %(asctime)s - %(levelname)s - %(message)s"
_log_datefmt = "%Y-%m-%d %H:%M:%S"

logger = logging.getLogger("Search Agent")
if not logger.handlers:
    _handler = logging.StreamHandler(sys.stdout)
    _handler.setFormatter(logging.Formatter(_log_format, _log_datefmt))
    logger.addHandler(_handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False


# ---------------------------------------------------------------------------
# 核心函数
# ---------------------------------------------------------------------------

def search_papers(query: str, max_results: int = 1) -> List[arxiv.Result]:
    """在 ArXiv 中搜索与关键词匹配的最新论文。

    Args:
        query: 学术关键词，例如 "photocatalytic materials water treatment"。
        max_results: 返回的最大论文数，默认 1。

    Returns:
        arxiv.Result 对象列表。
    """
    search = arxiv.Search(
        query=f"all:{query}",
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending,
    )

    client = arxiv.Client(
        page_size=100,
        delay_seconds=3,
        num_retries=5,
    )

    logger.info('🔍  Searching ArXiv for: "%s"', query)
    query = query.strip()
    results: List[arxiv.Result] = []

    try:
        for r in client.results(search):
            results.append(r)
    except Exception as e:
        logger.error("❌  ArXiv API 调用失败: %s", str(e))
        return results

    logger.info("✅  Found %d paper(s)", len(results))
    return results


def format_paper_info(result: arxiv.Result) -> str:
    """将论文元数据格式化为可读字符串。"""
    title = result.title.replace("\n", " ").strip()
    authors = ", ".join(a.name for a in result.authors)
    abstract = result.summary.replace("\n", " ").strip()

    lines = [
        f"📄  Title   : {title}",
        f"👥  Authors : {authors}",
        f"📂  Category: {result.primary_category}",
        f"🔗  ArXiv  : {result.entry_id}",
        f"📝  Abstract: {abstract[:300]}...",
    ]
    return "\n".join(lines)


def download_pdf(result: arxiv.Result, output_dir: str = "pdfs") -> Optional[str]:
    """下载论文 PDF 到本地目录。

    Args:
        result: arxiv.Result 对象。
        output_dir: PDF 存储目录，默认为 "pdfs"。

    Returns:
        本地 PDF 路径，失败则返回 None。
    """
    os.makedirs(output_dir, exist_ok=True)

    pdf_url = result.pdf_url
    if not pdf_url:
        logger.warning("⚠️  该论文无可用 PDF 链接")
        return None

    logger.info('⬇   Downloading PDF: %s', pdf_url)

    try:
        filepath = result.download_pdf(dirpath=output_dir)
        logger.info("✅  PDF saved to: %s", filepath)
        return filepath
    except Exception as e:
        logger.error("❌  Failed to download PDF: %s", str(e))
        return None


# ---------------------------------------------------------------------------
# CLI 入口
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Search Agent — 检索 ArXiv 论文并下载 PDF",
    )
    parser.add_argument(
        "-q", "--query",
        type=str,
        required=True,
        help='学术关键词，例如 "photocatalytic materials water treatment"',
    )
    parser.add_argument(
        "-n", "--num-results",
        type=int,
        default=1,
        help="返回的论文数量（默认: 1）",
    )
    parser.add_argument(
        "-o", "--output-dir",
        type=str,
        default="pdfs",
        help="PDF 下载目录（默认: pdfs）",
    )
    args = parser.parse_args()

    # Step 1: 搜索论文
    papers = search_papers(query=args.query, max_results=args.num_results)

    if not papers:
        logger.warning("⚠️  未找到任何匹配论文，退出。")
        sys.exit(1)

    # Step 2: 打印元数据 & 下载 PDF
    for i, paper in enumerate(papers, 1):
        logger.info("=" * 60)
        logger.info("Paper #%d", i)
        logger.info("=" * 60)
        for line in format_paper_info(paper).split("\n"):
            logger.info(line)

        logger.info("-" * 60)
        download_pdf(paper, output_dir=args.output_dir)
        logger.info("")

    logger.info("🎉  All done!")


if __name__ == "__main__":
    main()
