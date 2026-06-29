"""
消防审图工具 - 配置文件
修改 ZHIPU_API_KEY 为你的智谱API密钥
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ── 智谱GLM配置 ────────────────────────────────────────────────
ZHIPU_API_KEY: str = os.getenv("ZHIPU_API_KEY", "your_api_key_here")
ZHIPU_MODEL: str = os.getenv("ZHIPU_MODEL", "glm-4-plus")  # glm-4-plus / glm-z1-preview
ZHIPU_BASE_URL: str = os.getenv("ZHIPU_BASE_URL", "")  # 国际版填 https://open.bigmodel.cn/api/paas/v4/

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
