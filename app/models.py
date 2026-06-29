from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class ReviewRequest(BaseModel):
    # 项目基本信息
    site: str = Field(default="南宁宜家", description="站点名称")
    tenant_name: str = Field(default="", description="租户名称")
    floor: str = Field(..., description="楼层: B2/B1/1F/2F/3F")

    # 业态属性
    tenant_type_1: str = Field(..., description="一级业态")
    tenant_type_2: str = Field(..., description="二级业态")
    area: float = Field(..., gt=0, description="房间建筑面积(㎡)")
    ceiling_type: str = Field(..., description="吊顶类型")

    # 空间参数（用于排烟计算）
    ceiling_height: float = Field(default=3.5, gt=0, description="净空高度(m)")
    room_max_length: float = Field(default=0.0, ge=0, description="房间最长边尺寸(m)，0表示未知")

    # 改造条件（用于触发安全阀）
    change_fire_zone: bool = Field(default=False, description="是否改变防火分区主边界")
    change_smoke_zone: bool = Field(default=False, description="是否改变防烟分区主边界")
    complex_space: bool = Field(default=False, description="是否涉及中庭/步行街/异形大空间")

    # 影响项 / 改造项
    new_wall: bool = Field(default=False, description="新增隔墙/墙体")
    wall_to_ceiling: bool = Field(default=False, description="隔墙到顶（接近顶板）")
    new_enclosed_room: bool = Field(default=False, description="新增封闭房间")
    high_shelves: bool = Field(default=False, description="高柜/高货架")
    block_sprinkler: bool = Field(default=False, description="遮挡喷头")
    block_detector: bool = Field(default=False, description="遮挡探测器")
    block_smoke_vent: bool = Field(default=False, description="遮挡排烟口")
    block_hydrant: bool = Field(default=False, description="遮挡消火栓")
    block_evacuation_sign: bool = Field(default=False, description="遮挡疏散标志")


class ArticleRef(BaseModel):
    standard: str
    article: str
    title: str
    excerpt: str


class ModuleResult(BaseModel):
    module_name: str
    status: str  # "pass" | "warning" | "manual" | "violation"
    summary: str
    details: List[str]
    calculations: Optional[Dict[str, Any]] = None
    impacts: List[str] = Field(default_factory=list)   # 影响项触发的提醒
    references: List[ArticleRef] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)


class ReviewResult(BaseModel):
    # 第一层：总结论
    requires_manual: bool
    manual_reasons: List[str]
    overall_status: str   # "manual_required" | "review_complete"
    overall_summary: str

    # 第二层：各专业模块
    modules: Dict[str, ModuleResult]

    # 第三层高亮汇总
    highlights: List[str]

    # GLM生成的最终综合意见
    llm_opinion: Optional[str] = None


class ReportExportRequest(BaseModel):
    request: ReviewRequest
    result: ReviewResult
