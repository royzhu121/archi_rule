"""
消防审图规则引擎 - 六大专业模块
适用：耐火等级一级，多层民用建筑，商业综合体
     既有自动喷水灭火系统 + 既有火灾自动报警系统
     二次装修不改变防火分区/防烟分区主边界
"""

import math
import json
import os
from typing import Optional

from app.models import ReviewRequest, ReviewResult, ModuleResult, ArticleRef
from app.rules.tenant_profiles import get_profile, is_auto_reviewable

# 加载条文库
_ARTICLES_PATH = os.path.join(os.path.dirname(__file__), "..", "standards", "articles.json")
with open(_ARTICLES_PATH, "r", encoding="utf-8") as f:
    _ARTICLES_DB: dict = json.load(f)["articles"]


def _article(article_id: str) -> Optional[ArticleRef]:
    """从条文库取出指定条文"""
    a = _ARTICLES_DB.get(article_id)
    if not a:
        return None
    return ArticleRef(
        standard=a["standard"],
        article=a["article"],
        title=a["title"],
        excerpt=a["content"][:200] + ("..." if len(a["content"]) > 200 else ""),
    )


def _refs(*ids: str) -> list[ArticleRef]:
    return [ref for i in ids if (ref := _article(i)) is not None]


# ═══════════════════════════════════════════════════════════
#  触发人工复核检查
# ═══════════════════════════════════════════════════════════
def check_manual_triggers(req: ReviewRequest, profile: Optional[dict]) -> list[str]:
    reasons = []

    # 业态本身是高风险
    if profile and not profile.get("auto_review", False):
        reasons.append(profile.get("manual_reason", "业态属高风险，须人工复核"))

    # 防火分区/防烟分区被改变
    if req.change_fire_zone:
        reasons.append("改变了原防火分区主边界，超出自动审查范围，须转人工复核")
    if req.change_smoke_zone:
        reasons.append("改变了原防烟分区主边界，须转人工复核")
    if req.complex_space:
        reasons.append("涉及中庭/步行街/异形大空间等复杂场景，须转人工复核")

    return reasons


# ═══════════════════════════════════════════════════════════
#  5.1  内装修防火（GB50222-2017）
# ═══════════════════════════════════════════════════════════
def check_decoration(req: ReviewRequest, profile: dict) -> ModuleResult:
    details: list[str] = []
    impacts: list[str] = []
    suggestions: list[str] = []
    status = "pass"

    # 本建筑：一级耐火，既有喷淋+报警 → 顶棚以外可降一级（B1→B2）
    ceiling_required = "A级（不可降低）"
    wall_required = "B1级（有喷淋+报警可降至B2级）"
    floor_required = "B1级（有喷淋+报警可降至B2级）"
    partition_required = "B1级（有喷淋+报警可降至B2级）"

    details.append(f"✦ 本建筑耐火等级一级，既有自动喷水灭火系统及火灾自动报警系统")
    details.append(f"✦ 依据 GB50222-2017 第4.0.8条：顶棚须保持 A 级，其余部位可在 B1 基础上降一级至 B2 级")
    details.append(f"┌ 顶棚装修材料：{ceiling_required}")
    details.append(f"├ 墙面/隔断装修材料：{wall_required}")
    details.append(f"└ 地面装修材料：{floor_required}")
    details.append(f"✦ 疏散走道及安全出口界面：顶棚 A 级，墙面 A 级（从严控制，不可降级）")

    # 影响项处理
    if req.new_wall:
        impacts.append("⚠ 新增隔墙/墙体：隔墙面层装修材料不应低于 B1 级")
        suggestions.append("新增隔墙面层材料需满足 B1 级要求，靠近走道一侧不应低于 B1 级")
        status = "warning"
    if req.new_enclosed_room:
        impacts.append("⚠ 新增封闭房间：新房间内顶棚 A 级，其余可为 B2 级（有喷淋+报警）")
        status = "warning"

    refs = _refs("GB50222-2017_4.0.4", "GB50222-2017_4.0.8", "GB50222-2017_5.1.1")
    return ModuleResult(
        module_name="内装修防火",
        status=status,
        summary=f"顶棚须用 A 级材料；墙面/地面/隔断在本建筑条件下可用 B2 级，疏散走道界面从严",
        details=details,
        impacts=impacts,
        references=refs,
        suggestions=suggestions,
    )


# ═══════════════════════════════════════════════════════════
#  5.2  自动喷水灭火系统（GB50084-2017）
# ═══════════════════════════════════════════════════════════
def check_sprinkler(req: ReviewRequest, profile: dict) -> ModuleResult:
    details: list[str] = []
    impacts: list[str] = []
    suggestions: list[str] = []
    status = "pass"

    hazard = profile.get("sprinkler_hazard", "中危险级I")
    if hazard == "中危险级I":
        max_area = 12.5
        max_spacing = 3.6
        min_spacing = 1.8
    else:
        max_area = 11.5
        max_spacing = 3.4
        min_spacing = 1.8

    # 估算最少喷头数量
    min_heads = math.ceil(req.area / max_area)

    # 吊顶类型影响
    ceiling_note = ""
    if req.ceiling_type == "封闭式吊顶":
        ceiling_note = "封闭式吊顶：吊顶内和吊顶下方均应设置喷头"
        status = "warning"
    elif req.ceiling_type in ("通透吊顶，通透率>70%", "无吊顶"):
        ceiling_note = "通透率>70% 或无吊顶：喷头设于顶板下方即可"
    elif req.ceiling_type == "通透吊顶，通透率≤70%":
        ceiling_note = "通透率≤70%：视为封闭吊顶，吊顶上下均需设置喷头"
        status = "warning"

    details.append(f"✦ 业态危险等级：{hazard}（依 GB50084-2017 第6.1.1条）")
    details.append(f"✦ 每只喷头最大保护面积：{max_area} ㎡")
    details.append(f"✦ 喷头最大水平间距：{max_spacing} m，最小间距：{min_spacing} m")
    details.append(f"✦ 本租户面积 {req.area} ㎡，理论最少喷头数量：≥ {min_heads} 只")
    if ceiling_note:
        details.append(f"✦ 吊顶影响：{ceiling_note}")

    # 影响项处理
    if req.block_sprinkler:
        impacts.append("🚨 有遮挡喷头情形：必须整改，确保喷头无遮挡且水雾能到达保护区域")
        suggestions.append("遮挡喷头须立即整改：移除遮挡物或在遮挡物下方补设喷头")
        status = "violation"
    if req.wall_to_ceiling:
        impacts.append("⚠ 新增到顶隔墙：原喷头保护范围被分割，须在隔墙两侧分别校核，超范围时补设喷头")
        suggestions.append("到顶隔墙两侧各自核算喷头保护面积，不满足时补设")
        status = "warning" if status != "violation" else status
    if req.new_wall and not req.wall_to_ceiling:
        impacts.append("ℹ 新增隔断（未到顶）：通常不影响喷头保护范围，但需确认隔断高度不影响洒水效果")
    if req.high_shelves:
        impacts.append("⚠ 高柜/高货架：货架高度超过3.5m时，需在货架内补设货架型喷头")
        suggestions.append("货架高度>3.5m时，依 GB50084-2017 第7.1.4条在货架层内补设喷头")
        status = "warning" if status != "violation" else status

    refs = _refs("GB50084-2017_6.1.1", "GB50084-2017_7.2.1", "GB50084-2017_7.2.3", "GB50084-2017_7.2.4")
    return ModuleResult(
        module_name="自动喷水灭火系统",
        status=status,
        summary=f"危险等级 {hazard}，喷头间距≤{max_spacing}m，保护面积≤{max_area}㎡/只，估算≥{min_heads}只",
        details=details,
        calculations={"hazard_level": hazard, "max_area_per_head": max_area,
                      "max_spacing": max_spacing, "min_heads": min_heads},
        impacts=impacts,
        references=refs,
        suggestions=suggestions,
    )


# ═══════════════════════════════════════════════════════════
#  5.3  防烟排烟（GB51251-2017）
# ═══════════════════════════════════════════════════════════
def check_smoke_exhaust(req: ReviewRequest, profile: dict) -> ModuleResult:
    details: list[str] = []
    impacts: list[str] = []
    suggestions: list[str] = []
    status = "pass"

    area = req.area
    need_exhaust = area > 100  # 公共建筑>100㎡常有人停留

    # 排烟量计算（GB51251-2017 第4.6.3条）
    q_calc = 60 * area          # m³/h
    q_min = 15000               # m³/h
    q_design = max(q_calc, q_min)

    # 排烟口面积（风速按10m/s，GB51251-2017 第4.4.12条）
    vent_area = round(q_design / 36000, 2)   # m²

    # 排烟口数量（每个防烟分区至少1个，500㎡分区）
    vent_count = max(1, math.ceil(area / 500))

    # 挡烟垂壁高度（商业净空高度H，垂壁有效高度≥净空×0.1且≥500mm）
    smoke_curtain_height = max(0.5, round(req.ceiling_height * 0.1, 2))

    details.append(f"✦ 本租户面积 {area} ㎡，净空高度 {req.ceiling_height} m")
    if need_exhaust:
        details.append(f"✦ 面积>100㎡且常有人停留，须设置机械排烟（GB51251-2017 第4.1.4条）")
        details.append(f"")
        details.append(f"【排烟量计算步骤】")
        details.append(f"  ① 按面积计算：Q₁ = 60 × {area} = {q_calc:,.0f} m³/h")
        details.append(f"  ② 最小排烟量：Q_min = {q_min:,} m³/h")
        details.append(f"  ③ 设计排烟量：Q = max({q_calc:,.0f}, {q_min:,}) = {q_design:,.0f} m³/h")
        details.append(f"  ④ 排烟口设计面积：F = Q/(v×3600) = {q_design:,.0f}/(10×3600) = {vent_area} ㎡")
        details.append(f"  ⑤ 排烟口数量：不少于 {vent_count} 个（每防烟分区≥1个）")
        details.append(f"  ⑥ 挡烟垂壁有效高度：≥ {smoke_curtain_height} m（净空×10%，且≥500mm）")
        details.append(f"")
        details.append(f"✦ 补风量要求：不小于排烟量的50%，即补风量 ≥ {q_design*0.5:,.0f} m³/h")
        details.append(f"✦ 排烟口至最远点水平距离：不应超过30m（须在图纸上核实）")
    else:
        details.append(f"✦ 面积较小，可采用自然排烟（开口面积≥地面面积2%），须核实外窗情况")
        status = "warning"

    if req.block_smoke_vent:
        impacts.append("🚨 有遮挡排烟口情形：排烟口必须保持畅通，严禁遮挡")
        suggestions.append("立即移除排烟口遮挡物，排烟口周围300mm内不得有阻挡")
        status = "violation"
    if req.new_wall and req.wall_to_ceiling:
        impacts.append("⚠ 到顶隔墙可能分割防烟分区：新隔墙不得破坏原防烟分区主边界")
        suggestions.append("确认新隔墙未超越原挡烟垂壁边界；如有疑问转人工复核")
        status = "warning" if status != "violation" else status

    # 排烟口至最远点距离提醒
    if req.room_max_length > 30:
        impacts.append(f"⚠ 房间最长边 {req.room_max_length}m > 30m：须核实排烟口布置，确保覆盖最远点")
        status = "warning" if status != "violation" else status

    refs = _refs("GB51251-2017_4.1.4", "GB51251-2017_4.6.3", "GB51251-2017_4.4.12", "GB51251-2017_4.5.4")
    return ModuleResult(
        module_name="防烟排烟",
        status=status,
        summary=f"设计排烟量 {q_design:,.0f} m³/h，排烟口面积 ≥{vent_area} ㎡，数量 ≥{vent_count} 个",
        details=details,
        calculations={
            "need_exhaust": need_exhaust,
            "exhaust_volume_m3h": q_design,
            "vent_area_m2": vent_area,
            "vent_count": vent_count,
            "smoke_curtain_min_height_m": smoke_curtain_height,
            "supplemental_air_min_m3h": q_design * 0.5,
        },
        impacts=impacts,
        references=refs,
        suggestions=suggestions,
    )


# ═══════════════════════════════════════════════════════════
#  5.4  火灾自动报警（GB50116-2013）
# ═══════════════════════════════════════════════════════════
def check_alarm(req: ReviewRequest, profile: dict) -> ModuleResult:
    details: list[str] = []
    impacts: list[str] = []
    suggestions: list[str] = []
    status = "pass"

    detector_type = profile.get("detector_type", "感烟探测器")
    area = req.area

    # 探测器数量（GB50116-2013 第6.2.9条）
    # 感烟探测器，安装高度≤6m，θ<15°: A=80㎡, k=0.9
    A_detector = 80   # 保护面积 m²
    k = 0.9
    n_detectors = math.ceil(area / (k * A_detector))
    n_detectors = max(1, n_detectors)

    # 应急广播数量
    n_speakers = max(1, math.ceil(area / 150))  # 约150㎡/个
    speaker_power = "10W" if area > 100 else "3W"

    details.append(f"✦ 探测器类型：{detector_type}（依业态画像库选取）")
    details.append(f"✦ 保护面积 A = {A_detector} ㎡，修正系数 k = {k}（GB50116-2013 第6.2.9条）")
    details.append(f"✦ 探测器数量：N = ⌈{area} / ({k}×{A_detector})⌉ = ⌈{area/(k*A_detector):.2f}⌉ = {n_detectors} 只（最少）")
    details.append(f"✦ 应急广播：不少于 {n_speakers} 个，功率 {speaker_power}")
    details.append(f"✦ 手动报警按钮：任意点步行距离≤30m（需在平面图上校核）")
    details.append(f"✦ 本建筑已有火灾自动报警系统，二次装修须在原系统基础上增设或调整点位")

    if profile.get("level1") == "餐饮（使用明火）":
        details.append("✦ 明火餐饮特殊要求：厨房内需增设感温探测器；燃气使用区域需设可燃气体探测器")

    # 影响项
    if req.block_detector:
        impacts.append("🚨 有遮挡探测器情形：探测器视野被遮挡将导致漏报，须立即整改")
        suggestions.append("移除遮挡物或调整探测器位置，确保探测器下方水平距离500mm内无遮挡")
        status = "violation"
    if req.wall_to_ceiling:
        impacts.append("⚠ 到顶隔墙将房间分隔：每个新分隔区域需重新核算探测器数量并补充设置")
        suggestions.append("新分隔空间面积/0.9/80取整后，核实是否需要增设探测器")
        status = "warning" if status != "violation" else status
    if req.new_enclosed_room:
        impacts.append("⚠ 新增封闭房间：需在封闭房间内单独设置探测器、声光报警及广播")
        suggestions.append("封闭房间需独立设置报警点位，并校核声光报警及广播覆盖范围")
        status = "warning" if status != "violation" else status
    if req.room_max_length > 30:
        impacts.append(f"⚠ 房间最长边 {req.room_max_length}m > 30m：须核实手动报警按钮的步行距离覆盖")

    refs = _refs("GB50116-2013_6.2.2", "GB50116-2013_6.2.9", "GB50116-2013_6.4.1", "GB50116-2013_6.6.1")
    return ModuleResult(
        module_name="火灾自动报警",
        status=status,
        summary=f"{detector_type} ≥{n_detectors}只，应急广播 ≥{n_speakers}个（{speaker_power}）",
        details=details,
        calculations={
            "detector_type": detector_type,
            "detector_count_min": n_detectors,
            "speaker_count_min": n_speakers,
            "speaker_power": speaker_power,
        },
        impacts=impacts,
        references=refs,
        suggestions=suggestions,
    )


# ═══════════════════════════════════════════════════════════
#  5.5  消防应急照明和疏散指示（GB51309-2018）
# ═══════════════════════════════════════════════════════════
def check_evacuation_lighting(req: ReviewRequest, profile: dict) -> ModuleResult:
    details: list[str] = []
    impacts: list[str] = []
    suggestions: list[str] = []
    status = "pass"

    area = req.area
    room_length = req.room_max_length if req.room_max_length > 0 else math.sqrt(area)

    # 安全出口标志（每个疏散出口1个）
    exit_signs = max(1, math.ceil(area / 500))  # 简化估算

    # 疏散指示间距≤20m
    evacuation_signs = max(1, math.ceil(room_length / 20))

    # 标志规格
    sign_spec = "≥400mm×200mm（安装高度>3.5m）" if req.ceiling_height > 3.5 else "≥200mm×100mm（安装高度≤3.5m）"

    details.append(f"✦ 安全出口标志灯：每个疏散出口正上方各设1个，共 ≥{exit_signs} 个")
    details.append(f"✦ 标志灯规格：{sign_spec}（GB51309-2018 第3.2.9条）")
    details.append(f"✦ 疏散方向标志：沿疏散路径间距≤20m，依走道最长边 ~{room_length:.0f}m 估算 ≥{evacuation_signs} 个")
    details.append(f"✦ 标志灯安装高度：出口标志灯≥2.0m，疏散指示≤1.0m（墙面低位）")
    details.append(f"✦ 疏散路径须连续性，转角、袋形走道、视线中断处须补设指向标志")
    details.append(f"✦ 本建筑已有集中控制型应急照明系统，新增区域须接入原系统")

    if req.block_evacuation_sign:
        impacts.append("🚨 有遮挡疏散标志情形：疏散标志被遮挡将导致人员无法识别逃生路径，须立即整改")
        suggestions.append("立即移除遮挡疏散标志的物品；高柜、隔断不得遮挡疏散标志的可视范围")
        status = "violation"
    if req.new_wall or req.new_enclosed_room:
        impacts.append("⚠ 新增墙体/封闭房间：须重新检查疏散路径连续性，在新隔墙处补设疏散指示")
        suggestions.append("在新增隔墙处核实疏散路径是否被截断，必要时在隔墙上设置疏散指示标志")
        status = "warning" if status != "violation" else status

    refs = _refs("GB51309-2018_3.2.4", "GB51309-2018_3.2.9", "GB51309-2018_3.2.1")
    return ModuleResult(
        module_name="消防应急照明和疏散指示",
        status=status,
        summary=f"出口标志灯 ≥{exit_signs}个，疏散指示 ≥{evacuation_signs}个，规格{sign_spec}",
        details=details,
        calculations={
            "exit_sign_count_min": exit_signs,
            "evacuation_indicator_count_min": evacuation_signs,
            "sign_spec": sign_spec,
        },
        impacts=impacts,
        references=refs,
        suggestions=suggestions,
    )


# ═══════════════════════════════════════════════════════════
#  5.6  消火栓及灭火器（GB50974-2014 + GB50140-2005）
# ═══════════════════════════════════════════════════════════
def check_hydrant_extinguisher(req: ReviewRequest, profile: dict) -> ModuleResult:
    details: list[str] = []
    impacts: list[str] = []
    suggestions: list[str] = []
    status = "pass"

    fire_class = profile.get("fire_class", "A")
    area = req.area

    # Step1: 火灾类别确认
    if fire_class == "AE":
        fire_class_desc = "A类（固体可燃物）+ 需考虑E类（电气火灾）"
        extinguisher_type = "ABC干粉灭火器 + 酌情配置CO₂灭火器"
    else:
        fire_class_desc = "A类（固体可燃物）"
        extinguisher_type = "ABC干粉灭火器（3kg手提式）"

    # Step2: 保护距离（中危险级A类: 20m）
    protection_distance = 20

    # Step3: 配置数量（中危险级，每具保护面积75㎡，最少2具）
    n_extinguishers = max(2, math.ceil(area / 75))

    details.append(f"【Step 1 - 火灾类别确认】")
    details.append(f"  ✦ 火灾类别：{fire_class_desc}")
    details.append(f"  ✦ 推荐灭火器类型：{extinguisher_type}")
    details.append(f"")
    details.append(f"【Step 2 - 保护距离校核（GB50140-2005 第5.2.1条）】")
    details.append(f"  ✦ 中危险级保护距离：≤{protection_distance}m")
    details.append(f"  ✦ 需在平面图上核实：任意点到最近灭火器步行距离≤{protection_distance}m")
    details.append(f"")
    details.append(f"【Step 3 - 设置条件校核（GB50140-2005 第6.2.1条）】")
    details.append(f"  ✦ 最少灭火器数量：≥{n_extinguishers}具（面积{area}㎡，每具保护≤75㎡）")
    details.append(f"  ✦ 每个计算单元不少于2具")
    details.append(f"  ✦ 设置位置：明显可见、便于取用、不得堵塞疏散通道")
    details.append(f"")
    details.append(f"【消火栓底线要求（GB50974-2014 第7.4.2条）】")
    details.append(f"  ✦ 严禁对消火栓箱进行遮挡、包封或圈占")
    details.append(f"  ✦ 消火栓箱门须能在120°范围内自由开启")
    details.append(f"  ✦ 装修后须校核新平面下任一点的消火栓可达性（保护半径25m）")

    if req.block_hydrant:
        impacts.append("🚨 有遮挡消火栓情形：消火栓被遮挡属严重违规，须立即整改")
        suggestions.append("立即移除消火栓箱前的所有遮挡物，确保消火栓箱门可完全开启且操作空间满足要求")
        status = "violation"

    refs = _refs(
        "GB50974-2014_7.4.12", "GB50974-2014_7.4.2",
        "GB50140-2005_D.1", "GB50140-2005_5.2.1", "GB50140-2005_6.2.1"
    )
    return ModuleResult(
        module_name="消火栓及灭火器",
        status=status,
        summary=f"灭火器≥{n_extinguishers}具（{extinguisher_type}），保护距离≤{protection_distance}m，消火栓严禁遮挡",
        details=details,
        calculations={
            "fire_class": fire_class_desc,
            "extinguisher_type": extinguisher_type,
            "extinguisher_count_min": n_extinguishers,
            "protection_distance_m": protection_distance,
        },
        impacts=impacts,
        references=refs,
        suggestions=suggestions,
    )


# ═══════════════════════════════════════════════════════════
#  主入口：运行审图
# ═══════════════════════════════════════════════════════════
def run_review(req: ReviewRequest) -> ReviewResult:
    profile = get_profile(req.tenant_type_2)

    # 安全边界检查：强制触发人工复核
    manual_reasons = check_manual_triggers(req, profile)

    if manual_reasons:
        # 直接输出人工复核结论，不再做各专业计算
        return ReviewResult(
            requires_manual=True,
            manual_reasons=manual_reasons,
            overall_status="manual_required",
            overall_summary=(
                "【须转人工复核】本次审查触发了人工复核条件，"
                "系统不输出自动审查结论。请联系消防专业工程师进行完整审图。"
            ),
            modules={},
            highlights=[f"🔴 {r}" for r in manual_reasons],
        )

    if profile is None:
        profile = {
            "sprinkler_hazard": "中危险级I",
            "detector_type": "感烟探测器",
            "fire_class": "A",
            "decoration_space": "营业厅",
            "notes": [],
        }

    # 六大专业模块并行计算
    modules_result: dict[str, ModuleResult] = {
        "decoration": check_decoration(req, profile),
        "sprinkler": check_sprinkler(req, profile),
        "smoke_exhaust": check_smoke_exhaust(req, profile),
        "alarm": check_alarm(req, profile),
        "evacuation": check_evacuation_lighting(req, profile),
        "hydrant": check_hydrant_extinguisher(req, profile),
    }

    # 汇总高亮（收集所有影响项）
    highlights: list[str] = []
    has_violation = False
    for mod in modules_result.values():
        for impact in mod.impacts:
            highlights.append(f"[{mod.module_name}] {impact}")
        if mod.status == "violation":
            has_violation = True

    overall_status = "violation" if has_violation else "review_complete"
    overall_summary = (
        "【注意：存在违规项，须立即整改后方可施工】审查已完成，各专业结论见下方各模块。"
        "本工具结论仅供参考，任何情况下均须经消防专业工程师复核确认。"
        if has_violation else
        "【审查完成】各专业初步审查结论见下方各模块。"
        "本工具覆盖约80%常规租户场景，结论仅供参考，须经消防专业工程师复核确认，"
        "并应遵循规范条文及企业要求。"
    )

    return ReviewResult(
        requires_manual=False,
        manual_reasons=[],
        overall_status=overall_status,
        overall_summary=overall_summary,
        modules={k: v for k, v in modules_result.items()},
        highlights=highlights,
    )
