"""消防审图工具配置。API 密钥仅从环境变量读取。"""
import os
from dotenv import load_dotenv

load_dotenv()

# ── AI 配置 ────────────────────────────────────────────────────
MIMO_API_KEY: str = os.getenv("MIMO_API_KEY", "")
MIMO_MODEL: str = os.getenv("MIMO_MODEL", "mimo-v2.5-pro")
MIMO_BASE_URL: str = os.getenv("MIMO_BASE_URL", "https://api.xiaomimimo.com/v1").rstrip("/")

# 兼容旧部署；当未配置 MiMo 且存在 ZHIPU_API_KEY 时自动使用智谱。
ZHIPU_API_KEY: str = os.getenv("ZHIPU_API_KEY", "")
ZHIPU_MODEL: str = os.getenv("ZHIPU_MODEL", "glm-4-plus")
ZHIPU_BASE_URL: str = os.getenv(
    "ZHIPU_BASE_URL", "https://open.bigmodel.cn/api/paas/v4"
).rstrip("/")

AI_PROVIDER: str = os.getenv("AI_PROVIDER", "auto").strip().lower()
AI_TIMEOUT_SECONDS: float = float(os.getenv("AI_TIMEOUT_SECONDS", "45"))


def get_ai_config() -> dict[str, object]:
    """返回不含密钥值的生效配置，并保留旧智谱环境变量迁移路径。"""
    provider = AI_PROVIDER
    if provider == "auto":
        provider = "mimo" if MIMO_API_KEY else "zhipu" if ZHIPU_API_KEY else "mimo"
    if provider not in {"mimo", "zhipu"}:
        raise ValueError("AI_PROVIDER 仅支持 auto、mimo 或 zhipu")

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
