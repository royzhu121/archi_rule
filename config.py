"""
消防审图工具 - 配置文件
修改 QWEN_API_KEY 为你的千问 API 密钥
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ── 千问（DashScope 兼容模式）配置 ────────────────────────────
QWEN_API_KEY: str = os.getenv(
    "QWEN_API_KEY",
    os.getenv("DASHSCOPE_API_KEY", os.getenv("ALIYUN_API_KEY", "your_api_key_here")),
)
QWEN_MODEL: str = os.getenv("QWEN_MODEL", "qwen-plus")
QWEN_BASE_URL: str = os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")

# ── 项目默认值 ─────────────────────────────────────────────────
DEFAULT_SITE: str = "南宁宜家"
DEFAULT_FLOOR: str = "1F"

# ── 建筑基本条件（固定，贯穿全部规则） ─────────────────────────
BUILDING_CONTEXT = {
    "building_type": "多层民用建筑（商业综合体）",
    "fire_resistance_rating": "一级",
    "above_grade_fire_resistance": "一级",
    "below_grade_fire_resistance": "一级",
    "existing_sprinkler": True,
    "existing_alarm": True,
    "existing_smoke_exhaust": True,
    "description": (
        "本工具适用对象：耐火等级一级的大型商业综合体，"
        "地上地下耐火等级均为一级，既有消防设施完整，"
        "租户二次装修不改变防火分区及防烟分区主边界。"
    )
}

# ── 服务端口 ────────────────────────────────────────────────────
HOST: str = os.getenv("HOST", "0.0.0.0")
PORT: int = int(os.getenv("PORT", "8000"))
