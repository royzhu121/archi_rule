"""
业态画像库 - 租户二次消防审图工具
映射规则：二级业态 → 消防风险配置
适用建筑：耐火等级一级多层民用建筑（商业综合体）
"""

from typing import Optional

# ── 一级业态与二级业态的对应关系 ─────────────────────────────
LEVEL1_TO_LEVEL2: dict[str, list[str]] = {
    "普通商业零售类": [
        "服装/鞋履/箱包/化妆品/珠宝/钟表",
        "便利店/超市（无明火）",
    ],
    "餐饮（不使用明火）": [
        "中餐（无明火）",
        "西餐（无明火）",
        "中央厨房复热餐厅",
    ],
    "餐饮（使用明火）": [
        "中餐/西餐（明火）",
        "火锅/烧烤",
    ],
    "娱乐体验类": [
        "电影院",
        "KTV/电竞馆/密室逃脱/剧本杀",
    ],
    "儿童及教培类": [
        "儿童乐园",
        "儿童培训/亲子",
    ],
    "运动休闲类": [
        "健身房/瑜伽/攀岩",
    ],
    "生活服务及配套": [
        "银行/美容美发/后勤/仓储/设备",
    ],
}


# ── 二级业态画像库 ──────────────────────────────────────────
# auto_review: True = 可走自动审查；False = 直接转人工
# sprinkler_hazard: 喷淋危险等级（GB50084-2017）
# fire_class: 灭火器火灾类别（A=普通固体，E=电气）
# detector_type: 探测器类型

TENANT_PROFILES: dict[str, dict] = {

    "服装/鞋履/箱包/化妆品/珠宝/钟表": {
        "level1": "普通商业零售类",
        "fire_risk": "low",
        "sprinkler_hazard": "中危险级I",
        "sprinkler_head_type": "标准响应下垂型喷头",
        "sprinkler_temp_c": 68,
        "sprinkler_k_factor": "K=80",
        "fire_class": "A",
        "detector_type": "感烟探测器",
        "auto_review": True,
        "decoration_space": "营业厅",
        "notes": [],
        "description": "普通商业零售，可燃物荷载较低，无明火。",
    },

    "便利店/超市（无明火）": {
        "level1": "普通商业零售类",
        "fire_risk": "low",
        "sprinkler_hazard": "中危险级II",
        "sprinkler_head_type": "标准响应下垂型喷头（货架区可增设货架喷头）",
        "sprinkler_temp_c": 68,
        "sprinkler_k_factor": "K=80",
        "fire_class": "A",
        "detector_type": "感烟探测器",
        "auto_review": True,
        "decoration_space": "营业厅",
        "notes": ["超市货架高度大于3.5m时，需校核高货架喷头布置"],
        "description": "便利店/超市，商品陈列密度较高，注意货架影响喷头保护。",
    },

    "中餐（无明火）": {
        "level1": "餐饮（不使用明火）",
        "fire_risk": "medium_low",
        "sprinkler_hazard": "中危险级II",
        "sprinkler_head_type": "厨房区下垂型喷头",
        "sprinkler_temp_c": 93,
        "sprinkler_k_factor": "K=80",
        "fire_class": "A",
        "detector_type": "感烟探测器",
        "auto_review": True,
        "decoration_space": "营业厅",
        "notes": ["厨房区域应单独设置感温探测器", "厨房排油烟管道需做防火处理"],
        "description": "无明火中餐，厨房使用电磁炉等电热设备，注意油脂火灾风险。",
    },

    "西餐（无明火）": {
        "level1": "餐饮（不使用明火）",
        "fire_risk": "medium_low",
        "sprinkler_hazard": "中危险级II",
        "sprinkler_head_type": "厨房区下垂型喷头",
        "sprinkler_temp_c": 93,
        "sprinkler_k_factor": "K=80",
        "fire_class": "A",
        "detector_type": "感烟探测器",
        "auto_review": True,
        "decoration_space": "营业厅",
        "notes": ["厨房操作间需设置感温探测器"],
        "description": "无明火西餐，通常使用电热设备。",
    },

    "中央厨房复热餐厅": {
        "level1": "餐饮（不使用明火）",
        "fire_risk": "medium_low",
        "sprinkler_hazard": "中危险级II",
        "sprinkler_head_type": "复热及备餐区下垂型喷头",
        "sprinkler_temp_c": 79,
        "sprinkler_k_factor": "K=80",
        "fire_class": "A",
        "detector_type": "感烟探测器",
        "auto_review": True,
        "decoration_space": "营业厅",
        "notes": ["复热设备用电安全需核实", "复热区域单独设置感温探测器"],
        "description": "中央厨房供餐，现场仅做复热，电气负荷需关注。",
    },

    "中餐/西餐（明火）": {
        "level1": "餐饮（使用明火）",
        "fire_risk": "high",
        "sprinkler_hazard": "中危险级II",
        "sprinkler_head_type": "厨房区下垂型喷头（耐高温）",
        "sprinkler_temp_c": 93,
        "sprinkler_k_factor": "K=80",
        "fire_class": "A",
        "detector_type": "感温探测器",
        "auto_review": True,
        "manual_reason": "明火餐饮（燃气厨房）属高风险业态，存在爆燃风险，须转人工复核",
        "decoration_space": "营业厅",
        "notes": [],
        "description": "使用明火（燃气灶、卡式炉等），高风险。",
    },

    "火锅/烧烤": {
        "level1": "餐饮（使用明火）",
        "fire_risk": "very_high",
        "sprinkler_hazard": "中危险级II",
        "sprinkler_head_type": "就餐区标准喷头 + 明火区耐高温喷头",
        "sprinkler_temp_c": 93,
        "sprinkler_k_factor": "K=80",
        "fire_class": "A",
        "detector_type": "感温探测器",
        "auto_review": True,
        "manual_reason": "火锅/烧烤属高火灾风险明火业态，且涉及燃气、油脂，须转人工复核",
        "decoration_space": "营业厅",
        "notes": [],
        "description": "桌面明火（固体燃料/燃气），高火灾荷载。",
    },

    "电影院": {
        "level1": "娱乐体验类",
        "fire_risk": "high",
        "sprinkler_hazard": "中危险级II",
        "sprinkler_head_type": "标准响应下垂型喷头",
        "sprinkler_temp_c": 68,
        "sprinkler_k_factor": "K=80",
        "fire_class": "A",
        "detector_type": "感烟探测器",
        "auto_review": True,
        "manual_reason": "电影院属人员密集公共场所，疏散复杂，须转人工复核",
        "decoration_space": "营业厅",
        "notes": [],
        "description": "密闭放映空间，疏散要求高。",
    },

    "KTV/电竞馆/密室逃脱/剧本杀": {
        "level1": "娱乐体验类",
        "fire_risk": "high",
        "sprinkler_hazard": "中危险级II",
        "sprinkler_head_type": "标准响应下垂型喷头",
        "sprinkler_temp_c": 68,
        "sprinkler_k_factor": "K=80",
        "fire_class": "A",
        "detector_type": "感烟探测器",
        "auto_review": True,
        "manual_reason": "KTV/密室逃脱/剧本杀类场所疏散路径复杂，人员识路能力差，须转人工复核",
        "decoration_space": "营业厅",
        "notes": [],
        "description": "多隔间复杂布局，疏散指示要求特殊。",
    },

    "儿童乐园": {
        "level1": "儿童及教培类",
        "fire_risk": "high",
        "sprinkler_hazard": "中危险级II",
        "sprinkler_head_type": "快速响应下垂型喷头",
        "sprinkler_temp_c": 68,
        "sprinkler_k_factor": "K=80",
        "fire_class": "A",
        "detector_type": "感烟探测器",
        "auto_review": True,
        "manual_reason": "儿童活动场所，儿童自救能力弱，疏散标准特殊，须转人工复核",
        "decoration_space": "营业厅",
        "notes": [],
        "description": "儿童人群，需特殊疏散保障。",
    },

    "儿童培训/亲子": {
        "level1": "儿童及教培类",
        "fire_risk": "high",
        "sprinkler_hazard": "中危险级I",
        "sprinkler_head_type": "快速响应下垂型喷头",
        "sprinkler_temp_c": 68,
        "sprinkler_k_factor": "K=80",
        "fire_class": "A",
        "detector_type": "感烟探测器",
        "auto_review": True,
        "manual_reason": "儿童培训/亲子场所，须转人工复核",
        "decoration_space": "营业厅",
        "notes": [],
        "description": "有监护人陪同，但仍属儿童聚集场所。",
    },

    "健身房/瑜伽/攀岩": {
        "level1": "运动休闲类",
        "fire_risk": "low",
        "sprinkler_hazard": "中危险级I",
        "sprinkler_head_type": "标准响应下垂型喷头",
        "sprinkler_temp_c": 68,
        "sprinkler_k_factor": "K=80",
        "fire_class": "A",
        "detector_type": "感烟探测器",
        "auto_review": True,
        "decoration_space": "营业厅",
        "notes": ["大净空区域（攀岩）需核实排烟量及喷头安装高度"],
        "description": "运动休闲，可燃物较少，但注意大空间排烟。",
    },

    "银行/美容美发/后勤/仓储/设备": {
        "level1": "生活服务及配套",
        "fire_risk": "low",
        "sprinkler_hazard": "中危险级I",
        "sprinkler_head_type": "标准响应下垂型喷头（设备区按工艺复核）",
        "sprinkler_temp_c": 68,
        "sprinkler_k_factor": "K=80",
        "fire_class": "AE",
        "detector_type": "感烟探测器",
        "auto_review": True,
        "decoration_space": "营业厅",
        "notes": ["设备机房/电气集中区域需考虑E类火灾，酌情配置CO₂灭火器"],
        "description": "生活服务配套，电气设备相对集中时需关注E类火灾。",
    },
}


def get_profile(tenant_type_2: str) -> Optional[dict]:
    """根据二级业态名称获取画像，支持模糊匹配"""
    if tenant_type_2 in TENANT_PROFILES:
        return TENANT_PROFILES[tenant_type_2]
    # 模糊匹配
    for key, profile in TENANT_PROFILES.items():
        if tenant_type_2.replace(" ", "") in key.replace(" ", ""):
            return profile
    return None


def is_auto_reviewable(tenant_type_2: str) -> tuple[bool, str]:
    """
    返回 (可否自动审查, 不可审查原因)
    """
    profile = get_profile(tenant_type_2)
    if profile is None:
        return False, f"未知业态类型：{tenant_type_2}，须转人工复核"
    if not profile.get("auto_review", False):
        return False, profile.get("manual_reason", "该业态须转人工复核")
    return True, ""


def get_all_level2_by_level1(level1: str) -> list[str]:
    return LEVEL1_TO_LEVEL2.get(level1, [])
