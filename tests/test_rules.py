from app.models import ReviewRequest
from app.rules.engine import run_review
from app.rules.tenant_profiles import TENANT_PROFILES


def _request(tenant: str, level1: str) -> ReviewRequest:
    return ReviewRequest(
        floor="1F",
        tenant_type_1=level1,
        tenant_type_2=tenant,
        area=200,
        ceiling_type="通透吊顶，通透率>70%",
    )


def test_every_auto_profile_uses_its_fixed_project_design_hazard():
    for tenant, profile in TENANT_PROFILES.items():
        if not profile["auto_review"]:
            result = run_review(_request(tenant, profile["level1"]))
            assert result.requires_manual is True, tenant
            assert result.modules == {}, tenant
            continue
        assert profile["normative_sprinkler_hazard"] == profile["sprinkler_hazard"], tenant
        result = run_review(_request(tenant, profile["level1"]))
        sprinkler = result.modules["sprinkler"]
        assert sprinkler.calculations["hazard_level"] == profile["sprinkler_hazard"]
        assert "本项目原设计采用" in "\n".join(sprinkler.details)


def test_ordinary_mall_retail_is_medium_hazard_two_with_project_parameters():
    tenant = "服装/鞋履/箱包/化妆品/珠宝/钟表"
    result = run_review(_request(tenant, "普通商业零售类"))
    sprinkler = result.modules["sprinkler"]

    assert sprinkler.calculations["normative_hazard_level"] == "中危险级II"
    assert sprinkler.calculations["hazard_level"] == "中危险级II"
    assert sprinkler.calculations["max_area_per_head"] == 11.5
    assert sprinkler.calculations["max_spacing"] == 3.4
    assert sprinkler.calculations["design_parameters"]["spray_intensity"] == "8×1.3 L/(min·㎡)"
    assert sprinkler.calculations["design_parameters"]["action_area"] == "160㎡"
    assert sprinkler.calculations["design_parameters"]["design_flow"] == "30 L/s"
    assert sprinkler.calculations["design_parameters"]["k_factor"] == "K80"
    assert sprinkler.calculations["design_parameters"]["response"] == "快速响应"


def test_small_tenant_does_not_disable_existing_mechanical_smoke_exhaust():
    result = run_review(
        ReviewRequest(
            floor="1F",
            tenant_type_1="普通商业零售类",
            tenant_type_2="服装/鞋履/箱包/化妆品/珠宝/钟表",
            area=50,
            ceiling_type="无吊顶",
        )
    )
    smoke = result.modules["smoke_exhaust"]
    assert smoke.calculations["need_exhaust"] is True
    assert "自然排烟" not in "\n".join(smoke.details)


def test_unknown_and_out_of_boundary_cases_stop_for_manual_review():
    unknown = run_review(_request("独立街边小店", "普通商业零售类"))
    changed_boundary = run_review(
        _request("服装/鞋履/箱包/化妆品/珠宝/钟表", "普通商业零售类").model_copy(
            update={"change_fire_zone": True}
        )
    )
    assert unknown.requires_manual is True
    assert unknown.modules == {}
    assert changed_boundary.requires_manual is True
    assert changed_boundary.modules == {}


def test_mismatched_tenant_levels_cannot_bypass_profile_boundary():
    result = run_review(
        _request("服装/鞋履/箱包/化妆品/珠宝/钟表", "生活服务及配套")
    )
    assert result.requires_manual is True
    assert "不匹配" in result.manual_reasons[0]
