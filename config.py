import os
from dotenv import load_dotenv

# 加载 .env 文件（如果存在）
load_dotenv()

class Config:
    # LLM 相关
    LLM_API_KEY = os.getenv("LLM_API_KEY")
    LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
    LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "gpt-4o")

    # 路径配置
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    PDF_DIR = os.getenv("PDF_DIR", os.path.join(BASE_DIR, "pdfs"))
    OUTPUT_DIR = os.getenv("OUTPUT_DIR", os.path.join(BASE_DIR, "outputs"))

    # 解析配置
    MAX_CHARS = int(os.getenv("MAX_CHARS", 12000))

    @classmethod
    def validate(cls):
        """校验关键配置项"""
        missing = []
        if not cls.LLM_API_KEY:
            missing.append("LLM_API_KEY")
        return missing
