"""
parse_agent.py — 解析 Agent

职责：读取 PDF 文本 → 调用大模型 API 提取结构化参数 → 输出 JSON
"""

import argparse
import json
import logging
import os
import sys
import time
from glob import glob
from typing import Optional

import pdfplumber
from openai import OpenAI

# ---------------------------------------------------------------------------
# Logging 配置（独立 Handler，避免被主调度器重复配置）
# ---------------------------------------------------------------------------
_log_format = "[Parse Agent] %(asctime)s - %(levelname)s - %(message)s"
_log_datefmt = "%Y-%m-%d %H:%M:%S"

logger = logging.getLogger("Parse Agent")
if not logger.handlers:
    _handler = logging.StreamHandler(sys.stdout)
    _handler.setFormatter(logging.Formatter(_log_format, _log_datefmt))
    logger.addHandler(_handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False

# ---------------------------------------------------------------------------
# 环境变量 & 常量
# ---------------------------------------------------------------------------
ENV_API_KEY = "LLM_API_KEY"
ENV_BASE_URL = "LLM_BASE_URL"
ENV_MODEL_NAME = "LLM_MODEL_NAME"

DEFAULT_MAX_CHARS = 12000

# ---------------------------------------------------------------------------
# System Prompt
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """\
You are a senior materials science expert. Your task is to deeply analyze \
the given academic paper and extract structured information.

Extract the following fields and return ONLY a valid JSON object. \
Do NOT include markdown code blocks, explanations, or any text outside the JSON:

{
  "innovation": "A 1-2 sentence summary of the core innovation/contribution of this paper",
  "synthesis_conditions": "Key synthesis or preparation conditions (e.g. temperature, pressure, time, precursors, method). Return null if not applicable.",
  "performance_metrics": [
    {"metric": "metric name", "value": numeric_value_or_null, "unit": "unit string"}
  ]
}

- innovation: Concise 1-2 sentence summary of the core innovation.
- synthesis_conditions: Key preparation/synthesis parameters. null if N/A.
- performance_metrics: Array of objects. Each object has 'metric' (str), 'value' (number or null), 'unit' (str). Empty array if no metrics found.
"""


# ---------------------------------------------------------------------------
# PDF 文本提取
# ---------------------------------------------------------------------------

def read_pdf(filepath: str, max_chars: int = DEFAULT_MAX_CHARS) -> Optional[str]:
    """读取 PDF 并提取清洗后的纯文本。

    Args:
        filepath: PDF 文件路径。
        max_chars: 返回文本的最大字符数，超出部分截断。

    Returns:
        清洗后的文本字符串，失败则返回 None。
    """
    logger.info('📖  Reading PDF: %s', os.path.basename(filepath))

    try:
        with pdfplumber.open(filepath) as pdf:
            pages_text = []
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pages_text.append(text)
    except Exception as e:
        logger.error("❌  PDF read error: %s", str(e))
        return None

    if not pages_text:
        logger.warning("⚠️  No extractable text found (possibly scanned document)")
        return None

    raw = "\n".join(pages_text)

    # ---------- 文本清洗 ----------
    # 1. 统一换行符
    cleaned = raw.replace("\r\n", "\n")

    # 2. 移除不可打印字符（保留 \n \t 和空格）
    cleaned = "".join(
        c if c.isprintable() or c in "\n\t " else " " for c in cleaned
    )

    # 3. 合并跨行断句（学术 PDF 常见：一行内句子被截断）
    lines = cleaned.split("\n")
    processed_lines = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped == "":
            processed_lines.append("")
        elif stripped.endswith((".", "?", "!", ":", ";")):
            processed_lines.append(stripped)
        else:
            processed_lines.append(stripped + " ")

    cleaned = "\n".join(processed_lines)

    # 4. 压缩连续空行为一个
    while "\n\n\n" in cleaned:
        cleaned = cleaned.replace("\n\n\n", "\n\n")

    # 5. 截断
    if len(cleaned) > max_chars:
        logger.info("✂️  Truncated from %d to %d characters", len(cleaned), max_chars)
        cleaned = cleaned[:max_chars]

    logger.info("✅  Extracted %d characters from %s", len(cleaned), os.path.basename(filepath))
    return cleaned


# ---------------------------------------------------------------------------
# LLM API 调用
# ---------------------------------------------------------------------------

def _build_llm_client() -> Optional[tuple[OpenAI, str]]:
    """从环境变量读取配置并构建 OpenAI 客户端。"""
    api_key = os.environ.get(ENV_API_KEY)
    base_url = os.environ.get(ENV_BASE_URL)
    model = os.environ.get(ENV_MODEL_NAME)

    missing = [v for v in [ENV_API_KEY, ENV_BASE_URL, ENV_MODEL_NAME]
               if not os.environ.get(v)]
    if missing:
        logger.error(
            "❌  Missing environment variables: %s\n"
            "    Please set them before running, e.g.:\n"
            "    set %s=sk-your-key\n"
            "    set %s=https://api.example.com/v1\n"
            "    set %s=your-model-name",
            ", ".join(missing), ENV_API_KEY, ENV_BASE_URL, ENV_MODEL_NAME,
        )
        return None

    return OpenAI(base_url=base_url, api_key=api_key), model


def call_llm(system_prompt: str, user_text: str, max_retries: int = 3) -> Optional[str]:
    """调用 OpenAI 兼容 API。

    Args:
        system_prompt: 系统角色指令。
        user_text: 用户输入文本（论文内容）。
        max_retries: 最大重试次数。

    Returns:
        API 返回的原始文本，失败则返回 None。
    """
    client_info = _build_llm_client()
    if client_info is None:
        return None
    client, model = client_info

    logger.info('🤖  Calling LLM (model=%s, max_retries=%d)...', model, max_retries)

    for attempt in range(1, max_retries + 1):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_text},
                ],
                temperature=0.1,
            )

            content = response.choices[0].message.content
            if content is None:
                logger.warning("⚠️  LLM returned empty content on attempt %d/%d", attempt, max_retries)
                continue

            logger.info("✅  LLM response received (%d characters)", len(content))

            # 记录 token 用量（如 API 返回）
            if response.usage:
                logger.info(
                    "📊  Token usage — prompt: %d, completion: %d, total: %d",
                    response.usage.prompt_tokens,
                    response.usage.completion_tokens,
                    response.usage.total_tokens,
                )

            return content

        except Exception as e:
            logger.warning(
                "⚠️  LLM API attempt %d/%d failed: %s",
                attempt, max_retries, str(e),
            )
            if attempt < max_retries:
                logger.info("🔄  Retrying in 3 seconds...")
                time.sleep(3)
            else:
                logger.error("❌  LLM API failed after %d attempts", max_retries)
                return None

    return None


# ---------------------------------------------------------------------------
# JSON 解析
# ---------------------------------------------------------------------------

def parse_json_response(raw: str) -> dict:
    """解析 LLM 返回的 JSON，自动剥离 markdown 代码块包裹。

    Args:
        raw: LLM 返回的原始字符串。

    Returns:
        解析后的 dict；若解析失败则返回含 error 信息的 dict。
    """
    if not raw or not raw.strip():
        return {"error": "empty_response"}

    text = raw.strip()

    # 去除 ```json ... ``` 或 ``` ... ``` 包裹
    if text.startswith("```"):
        first_newline = text.find("\n")
        last_backtick = text.rfind("```")
        if first_newline != -1 and last_backtick != -1:
            text = text[first_newline:last_backtick].strip()
        elif last_backtick != -1:
            text = text[3:last_backtick].strip()
        else:
            text = text[3:].strip()

    # 尝试标准解析
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            logger.info("📋  JSON parsed: innovation / synthesis_conditions / performance_metrics")
            return data
        logger.warning("⚠️  JSON parsed but root is not a dict (type=%s)", type(data).__name__)
        return {"error": "root_not_dict", "data": data}
    except json.JSONDecodeError:
        pass

    # 容错：尝试提取最外层 { ... } 包裹的内容
    brace_start = text.find("{")
    brace_end = text.rfind("}")
    if brace_start != -1 and brace_end != -1 and brace_end > brace_start:
        try:
            data = json.loads(text[brace_start : brace_end + 1])
            if isinstance(data, dict):
                logger.info("📋  JSON parsed (extracted from braces)")
                return data
        except json.JSONDecodeError:
            pass

    logger.error("❌  JSON parse failed — raw preview: %s ...", text[:200])
    return {"error": "parse_failed", "raw_preview": text[:500]}


# ---------------------------------------------------------------------------
# 核心管线
# ---------------------------------------------------------------------------

def extract_paper_info(pdf_path: str, max_chars: int = DEFAULT_MAX_CHARS) -> dict:
    """完整管线：读取 PDF → LLM 解析 → JSON 返回。

    Args:
        pdf_path: PDF 文件路径。
        max_chars: 传递给 LLM 的最大字符数。

    Returns:
        包含文件信息和解析结果的 dict。
    """
    filename = os.path.basename(pdf_path)
    logger.info("=" * 60)
    logger.info("📄  Processing: %s", filename)
    logger.info("=" * 60)

    # Step 1: 读取 PDF
    text = read_pdf(pdf_path, max_chars=max_chars)
    if text is None:
        return {"file": filename, "error": "pdf_read_failed"}

    # Step 2: 调用 LLM
    response = call_llm(SYSTEM_PROMPT, text)
    if response is None:
        return {"file": filename, "error": "llm_call_failed"}

    # Step 3: 解析 JSON
    result = parse_json_response(response)
    result["file"] = filename
    return result


# ---------------------------------------------------------------------------
# CLI 入口
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Parse Agent — 读取 PDF → LLM 结构化解析 → JSON 输出",
    )
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--pdf", type=str, help="单篇 PDF 文件路径")
    target.add_argument("--dir", type=str, help="批量处理目录下的所有 PDF")
    parser.add_argument("--output", "-o", type=str, default=None,
                        help="输出 JSON 文件路径（可选）")
    parser.add_argument("--max-chars", type=int, default=DEFAULT_MAX_CHARS,
                        help=f"LLM 输入最大字符数（默认: {DEFAULT_MAX_CHARS})")
    args = parser.parse_args()

    # 收集待处理 PDF
    if args.pdf:
        pdf_files = [args.pdf]
        logger.info("📄  Target: single PDF — %s", args.pdf)
    else:
        pdf_files = sorted(glob(os.path.join(args.dir, "*.pdf")))
        if not pdf_files:
            logger.warning("⚠️  No PDF files found in %s", args.dir)
            sys.exit(1)
        logger.info("📂  Found %d PDF(s) in %s", len(pdf_files), args.dir)

    # 逐个处理
    results = []
    for pdf_path in pdf_files:
        result = extract_paper_info(pdf_path, max_chars=args.max_chars)
        results.append(result)

        if "error" not in result:
            print("\n" + json.dumps(result, ensure_ascii=False, indent=2) + "\n")
        else:
            logger.warning("⚠️  Skipped %s: %s",
                           os.path.basename(pdf_path), result["error"])

    # 批量输出到文件
    if args.output:
        os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        logger.info("💾  Results saved to: %s", args.output)

    logger.info("🎉  All done! Processed %d paper(s).", len(results))


if __name__ == "__main__":
    main()
