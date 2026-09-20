"""
业态画像库 - 租户二次消防审图工具
映射规则：二级业态 → 消防风险配置
适用建筑：耐火等级一级多层民用建筑（商业综合体）

所有画像均受固定建筑边界约束。normative_sprinkler_hazard 表示在本大型商业
综合体语境下的审查分类；sprinkler_hazard / sprinkler_design 表示项目原设计
采用值。项目参数仅用于本项目既有系统校核，不作为其他项目的通用参数。
"""

from typing import Optional


PROJECT_MALL_SHOP = {
    "area": "MALL商铺（餐饮一层、二层，净高约6m）",
    "system_type": "湿式",
    "hazard": "中危险级II",
    "spray_intensity": "8×1.3 L/(min·㎡)",
    "action_area": "160㎡",
    "design_flow": "30 L/s",
    "k_factor": "K80",
    "temperature": "68℃或93℃",
    "orientation": "直立型",
    "response": "快速响应",
    "ceiling": "通透吊顶",
}

PROJECT_SMALL_GOODS = {
    "area": "小商品销售区",
    "system_type": "湿式",
    "hazard": "中危险级II",
    "spray_intensity": "16.3 L/(min·㎡)",
    "action_area": "232㎡",
    "design_flow": "70 L/s",
    "k_factor": "K115",
    "temperature": "68℃",
    "orientation": "直立型",
    "response": "快速响应",
}

PROJECT_DISPLAY = {
    "area": "展示区",
    "system_type": "湿式",
    "hazard": "中危险级II",
    "spray_intensity": "12.2 L/(min·㎡)",
    "action_area": "232㎡",
    "design_flow": "60 L/s",
    "k_factor": "K115",
    "temperature": "68℃",
    "orientation": "直立型",
    "response": "快速响应",
}

PROJECT_RESTAURANT = {
    "area": "餐厅部",
    "system_type": "湿式",
    "hazard": "中危险级II",
    "spray_intensity": "8×1.3 L/(min·㎡)",
    "action_area": "160㎡",
    "design_flow": "30 L/s",
    "k_factor": "K80",
    "temperature": "68℃或93℃",
    "orientation": "直立型",
    "response": "快速响应",
    "ceiling": "格栅吊顶",
}

PROJECT_OFFICE = {
    "area": "办公区",
    "system_type": "湿式",
    "hazard": "中危险级I",
    "spray_intensity": "6 L/(min·㎡)",
    "action_area": "232㎡",
    "design_flow": "30 L/s",
    "k_factor": "K80",
    "temperature": "68℃",
    "orientation": "下垂型",
    "response": "快速响应",
    "ceiling": "密实吊顶",
}

PROJECT_EQUIPMENT_ROOM = {
    "area": "设备机房",
    "system_type": "湿式",
    "hazard": "中危险级II",
    "spray_intensity": "8 L/(min·㎡)",
    "action_area": "160㎡",
    "design_flow": "30 L/s",
    "k_factor": "K80",
    "temperature": "68℃",
    "orientation": "直立型",
    "response": "标准响应",
}

PROJECT_UNDERGROUND_GARAGE = {
    "area": "地下车库",
    "system_type": "湿式",
    "hazard": "中危险级II",
    "spray_intensity": "8 L/(min·㎡)",
    "action_area": "160㎡",
    "design_flow": "30 L/s",
    "k_factor": "K80",
    "temperature": "68℃",
    "orientation": "直立型",
    "response": "标准响应",
}

PROJECT_WAREHOUSE = {
    "area": "大件物品自提区、收银/折扣区或卸货区",
    "system_type": "湿式",
    "hazard": "仓库危险级II",
    "design_flow": "100或150 L/s（按净高及区域）",
    "k_factor": "K363",
    "temperature": "74℃或101℃（按净高及区域）",
    "orientation": "下垂型",
    "response": "快速响应",
    "design_heads": "12只",
    "note": "设计说明按区域和净高分别采用0.17MPa或0.41MPa；必须按原设计分区复核。",
    "zones": [
        {
            "area": "大件物品自提区（二层，净高6m）",
            "pressure": "0.17MPa",
            "design_flow": "100 L/s",
            "temperature": "74℃",
            "storage_height": "4.2m",
        },
        {
            "area": "大件物品自提区（一层，净高12m）",
            "pressure": "0.41MPa",
            "design_flow": "150 L/s",
            "temperature": "101℃",
            "storage_height": "9.1m",
        },
        {
            "area": "收银区/折扣区",
            "pressure": "0.41MPa",
            "design_flow": "150 L/s",
            "temperature": "74℃",
        },
        {
            "area": "卸货区",
            "pressure": "0.41MPa",
            "design_flow": "150 L/s",
            "temperature": "74℃",
        },
    ],
}

PROJECT_SPRINKLER_DESIGNS = {
    "地下车库": PROJECT_UNDERGROUND_GARAGE,
    "设备机房": PROJECT_EQUIPMENT_ROOM,
    "MALL商铺": PROJECT_MALL_SHOP,
    "仓储及物流区域": PROJECT_WAREHOUSE,
    "小商品销售区": PROJECT_SMALL_GOODS,
    "展示区": PROJECT_DISPLAY,
    "餐厅部": PROJECT_RESTAURANT,
    "办公区": PROJECT_OFFICE,
}


# ── 一级业态与二级业态的对应关系 ─────────────────────────────
LEVEL1_TO_LEVEL2: dict[str, list[str]] = {
    "普通商业零售类": [
        "服装/鞋履/箱包/化妆品/珠宝/钟表",
        "便利店/超市（无明火）",
        "小商品销售区",
        "展示区",
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
        "银行/美容美发/后勤",
        "办公区",
        "设备机房",
        "仓储/大件物品自提/收银折扣/卸货",
        "银行/美容美发/后勤/仓储/设备",
    ],
}


def _profile(
    *,
    level1: str,
    fire_risk: str,
    normative_hazard: str,
    design: dict,
    description: str,
    fire_class: str = "A",
    detector_type: str = "感烟探测器",
    auto_review: bool = True,
    notes: Optional[list[str]] = None,
    manual_reason: Optional[str] = None,
) -> dict:
    """构造统一画像，并保留 sprinkler_hazard 兼容现有 API。"""
    profile = {
        "level1": level1,
        "fire_risk": fire_risk,
        "normative_sprinkler_hazard": normative_hazard,
        "sprinkler_hazard": design["hazard"],
        "sprinkler_design": design,
        "sprinkler_basis": "项目设计说明",
        "fire_class": fire_class,
        "detector_type": detector_type,
        "auto_review": auto_review,
        "decoration_space": "营业厅",
        "notes": notes or [],
        "description": description,
    }
    if manual_reason:
        profile["manual_reason"] = manual_reason
    return profile


# ── 二级业态画像库 ──────────────────────────────────────────
TENANT_PROFILES: dict[str, dict] = {
    "服装/鞋履/箱包/化妆品/珠宝/钟表": _profile(
        level1="普通商业零售类",
        fire_risk="low",
        normative_hazard="中危险级II",
        design=PROJECT_MALL_SHOP,
        description="本大型商业综合体总建筑面积超过5000㎡，普通MALL零售商铺按中危险级II及项目设计参数校核。",
    ),
    "便利店/超市（无明火）": _profile(
        level1="普通商业零售类",
        fire_risk="low",
        normative_hazard="中危险级II",
        design=PROJECT_MALL_SHOP,
        description="本大型商业综合体内非仓储式便利店/超市按MALL商铺中危险级II基准校核；储存条件变化时转人工。",
        notes=["货架或储存方式改变时，不得沿用普通商铺参数，应按实际货物与堆高人工复核"],
    ),
    "小商品销售区": _profile(
        level1="普通商业零售类",
        fire_risk="medium",
        normative_hazard="中危险级II",
        design=PROJECT_SMALL_GOODS,
        description="项目设计说明单列的小商品销售区，按其增强设计参数校核。",
    ),
    "展示区": _profile(
        level1="普通商业零售类",
        fire_risk="medium",
        normative_hazard="中危险级II",
        design=PROJECT_DISPLAY,
        description="项目设计说明单列的展示区，按其增强设计参数校核。",
    ),
    "中餐（无明火）": _profile(
        level1="餐饮（不使用明火）",
        fire_risk="medium_low",
        normative_hazard="中危险级II",
        design=PROJECT_RESTAURANT,
        description="本大型商业综合体内无明火餐饮按餐厅部中危险级II及项目设计参数校核。",
        notes=["厨房区域应单独设置感温探测器", "厨房排油烟管道需做防火处理"],
    ),
    "西餐（无明火）": _profile(
        level1="餐饮（不使用明火）",
        fire_risk="medium_low",
        normative_hazard="中危险级II",
        design=PROJECT_RESTAURANT,
        description="本大型商业综合体内无明火餐饮按餐厅部中危险级II及项目设计参数校核。",
        notes=["厨房操作间需设置感温探测器"],
    ),
    "中央厨房复热餐厅": _profile(
        level1="餐饮（不使用明火）",
        fire_risk="medium",
        normative_hazard="中危险级II",
        design=PROJECT_RESTAURANT,
        description="含厨房的餐馆按中危险级II，本项目餐厅部原设计亦按中危险级II校核。",
        notes=["复热设备用电安全需核实", "复热区域单独设置感温探测器"],
    ),
    "中餐/西餐（明火）": _profile(
        level1="餐饮（使用明火）",
        fire_risk="high",
        normative_hazard="中危险级II",
        design=PROJECT_RESTAURANT,
        detector_type="感温探测器",
        auto_review=False,
        manual_reason="明火餐饮（燃气厨房）属高风险业态，存在爆燃风险，须转人工复核",
        description="餐馆（含厨房）为中危险级II；明火及燃气风险另行人工复核。",
    ),
    "火锅/烧烤": _profile(
        level1="餐饮（使用明火）",
        fire_risk="very_high",
        normative_hazard="中危险级II",
        design=PROJECT_RESTAURANT,
        detector_type="感温探测器",
        auto_review=False,
        manual_reason="火锅/烧烤属高火灾风险明火业态，且涉及燃气、油脂，须转人工复核",
        description="餐馆（含厨房）为中危险级II；桌面明火、燃气及油脂风险另行人工复核。",
    ),
    "电影院": _profile(
        level1="娱乐体验类",
        fire_risk="high",
        normative_hazard="须结合用途、火灾荷载及空间条件复核",
        design=PROJECT_MALL_SHOP,
        auto_review=False,
        manual_reason="电影院属人员密集公共场所，疏散复杂，须转人工复核",
        description="不得仅按普通商铺定级，须结合具体影厅条件和原设计人工复核。",
    ),
    "KTV/电竞馆/密室逃脱/剧本杀": _profile(
        level1="娱乐体验类",
        fire_risk="high",
        normative_hazard="须结合用途、火灾荷载及空间条件复核",
        design=PROJECT_MALL_SHOP,
        auto_review=False,
        manual_reason="KTV/密室逃脱/剧本杀类场所疏散路径复杂，人员识路能力差，须转人工复核",
        description="不得仅按普通商铺定级，多隔间及可燃荷载须人工复核。",
    ),
    "儿童乐园": _profile(
        level1="儿童及教培类",
        fire_risk="high",
        normative_hazard="须结合用途、火灾荷载及空间条件复核",
        design=PROJECT_MALL_SHOP,
        auto_review=False,
        manual_reason="儿童活动场所，儿童自救能力弱，疏散标准特殊，须转人工复核",
        description="游乐设施可燃荷载及空间条件差异大，须结合原设计人工复核。",
    ),
    "儿童培训/亲子": _profile(
        level1="儿童及教培类",
        fire_risk="high",
        normative_hazard="须结合用途、火灾荷载及空间条件复核",
        design=PROJECT_MALL_SHOP,
        auto_review=False,
        manual_reason="儿童培训/亲子场所，须转人工复核",
        description="儿童活动场所须结合具体用途、荷载和空间条件人工复核。",
    ),
    "健身房/瑜伽/攀岩": _profile(
        level1="运动休闲类",
        fire_risk="low",
        normative_hazard="中危险级II",
        design=PROJECT_MALL_SHOP,
        description="本大型商业综合体内运动休闲租户按MALL商铺中危险级II基准校核；攀岩等大空间另行人工复核。",
        notes=["攀岩等大净空区域需核实排烟量、喷头安装高度和原系统适用性"],
    ),
    "银行/美容美发/后勤": _profile(
        level1="生活服务及配套",
        fire_risk="low",
        normative_hazard="中危险级I",
        design=PROJECT_OFFICE,
        fire_class="AE",
        description="办公及普通服务空间按中危险级I，并按项目办公区原设计参数校核。",
        notes=["电气集中区域需考虑E类火灾"],
    ),
    "办公区": _profile(
        level1="生活服务及配套",
        fire_risk="low",
        normative_hazard="中危险级I",
        design=PROJECT_OFFICE,
        fire_class="AE",
        description="办公楼规范分类及项目办公区原设计均为中危险级I。",
    ),
    "设备机房": _profile(
        level1="生活服务及配套",
        fire_risk="medium",
        normative_hazard="中危险级II",
        design=PROJECT_EQUIPMENT_ROOM,
        fire_class="E",
        description="按项目设计说明设备机房参数校核，并关注电气火灾适配。",
    ),
    "仓储/大件物品自提/收银折扣/卸货": _profile(
        level1="生活服务及配套",
        fire_risk="high",
        normative_hazard="仓库危险级II",
        design=PROJECT_WAREHOUSE,
        auto_review=False,
        manual_reason="仓储及大件货物区域对货物类别、净高和堆高敏感，须按原设计分区人工复核",
        description="项目设计说明按仓库危险级II并依净高、区域采用不同参数，禁止套用普通商铺参数。",
    ),
    # 保留旧客户端可能提交的组合值；由于含办公、设备和仓储三种等级，禁止自动猜测。
    "银行/美容美发/后勤/仓储/设备": _profile(
        level1="生活服务及配套",
        fire_risk="high",
        normative_hazard="须按实际空间在中危险级I、中危险级II或仓库危险级II中确定",
        design=PROJECT_EQUIPMENT_ROOM,
        fire_class="AE",
        auto_review=False,
        manual_reason="该旧版组合业态包含办公、设备机房及仓储等不同喷淋等级，请按实际用途拆分后人工复核",
        description="兼容旧版API输入；不得将办公、设备机房和仓储统一映射为同一危险等级。",
    ),
}


def get_profile(tenant_type_2: str) -> Optional[dict]:
    """根据二级业态名称获取画像，支持模糊匹配。"""
    if tenant_type_2 in TENANT_PROFILES:
        return TENANT_PROFILES[tenant_type_2]
    for key, profile in TENANT_PROFILES.items():
        if tenant_type_2.replace(" ", "") in key.replace(" ", ""):
            return profile
    return None


def is_auto_reviewable(tenant_type_2: str) -> tuple[bool, str]:
    """返回 (可否自动审查, 不可审查原因)。"""
    profile = get_profile(tenant_type_2)
    if profile is None:
        return False, f"未知业态类型：{tenant_type_2}，须转人工复核"
    if not profile.get("auto_review", False):
        return False, profile.get("manual_reason", "该业态须转人工复核")
    return True, ""


def get_all_level2_by_level1(level1: str) -> list[str]:
    return LEVEL1_TO_LEVEL2.get(level1, [])
