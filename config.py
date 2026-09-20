"""消防审图工具配置。API 密钥仅从环境变量读取。"""
import os
from dotenv import load_dotenv

load_dotenv()

# ── AI 配置 ────────────────────────────────────────────────────
MIMO_API_KEY: str = os.getenv("MIMO_API_KEY", "")
MIMO_MODEL: str = os.getenv("MIMO_MODEL", "mimo-v2.5-pro")
MIMO_BASE_URL: str = os.getenv("MIMO_BASE_URL", "https://api.xiaomimimo.com/v1").rstrip("/")

QWEN_API_KEY: str = os.getenv("QWEN_API_KEY") or os.getenv("DASHSCOPE_API_KEY", "")
QWEN_MODEL: str = os.getenv("QWEN_MODEL", "qwen-plus")
QWEN_BASE_URL: str = os.getenv(
    "QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"
).rstrip("/")

# 兼容旧智谱部署。
ZHIPU_API_KEY: str = os.getenv("ZHIPU_API_KEY", "")
ZHIPU_MODEL: str = os.getenv("ZHIPU_MODEL", "glm-4-plus")
ZHIPU_BASE_URL: str = os.getenv(
    "ZHIPU_BASE_URL", "https://open.bigmodel.cn/api/paas/v4"
).rstrip("/")

AI_PROVIDER: str = os.getenv("AI_PROVIDER", "auto").strip().lower()
AI_TIMEOUT_SECONDS: float = float(os.getenv("AI_TIMEOUT_SECONDS", "45"))


def get_ai_config() -> dict[str, object]:
    """返回生效配置；auto 按千问、MiMo、智谱的顺序选择已配置项。"""
    provider = AI_PROVIDER
    if provider == "auto":
        if QWEN_API_KEY:
            provider = "qwen"
        elif MIMO_API_KEY:
            provider = "mimo"
        elif ZHIPU_API_KEY:
            provider = "zhipu"
        else:
            provider = "qwen"
    if provider not in {"qwen", "mimo", "zhipu"}:
        raise ValueError("AI_PROVIDER 仅支持 auto、qwen、mimo 或 zhipu")

    if provider == "qwen":
        return {
            "provider": "qwen",
            "api_key": QWEN_API_KEY,
            "model": QWEN_MODEL,
            "base_url": QWEN_BASE_URL,
            "configured": bool(QWEN_API_KEY),
        }
    if provider == "mimo":
        return {
            "provider": "mimo",
            "api_key": MIMO_API_KEY,
            "model": MIMO_MODEL,
            "base_url": MIMO_BASE_URL,
            "configured": bool(MIMO_API_KEY),
        }
    return {
        "provider": "zhipu",
        "api_key": ZHIPU_API_KEY,
        "model": ZHIPU_MODEL,
        "base_url": ZHIPU_BASE_URL,
        "configured": bool(ZHIPU_API_KEY),
    }

# ── 项目默认值 ─────────────────────────────────────────────────
DEFAULT_SITE: str = "南宁宜家"
DEFAULT_FLOOR: str = "1F"

# ── 建筑基本条件（固定，贯穿全部规则） ─────────────────────────
BUILDING_CONTEXT = {
    "building_type": "已建成投运的大型商业综合体（多层民用建筑）",
    "fire_resistance_rating": "一级",
    "above_grade_fire_resistance": "一级",
    "below_grade_fire_resistance": "一级",
    "existing_sprinkler": True,
    "existing_alarm": True,
    "existing_smoke_exhaust": True,
    "existing_hydrant": True,
    "scope": "租户二次装修快速审查",
    "changes_main_fire_or_smoke_zone_boundary": False,
    "description": (
        "本工具适用对象：耐火等级一级的大型商业综合体，"
        "地上地下耐火等级均为一级，既有消防设施完整，"
        "租户二次装修不改变防火分区及防烟分区主边界。"
    )
}

# ── 服务端口 ────────────────────────────────────────────────────
HOST: str = os.getenv("HOST", "0.0.0.0")
PORT: int = int(os.getenv("PORT", "8000"))
