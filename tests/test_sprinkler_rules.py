import unittest

from app.models import ReviewRequest
from app.rules.engine import check_sprinkler
from app.rules.tenant_profiles import (
    LEVEL1_TO_LEVEL2,
    PROJECT_SPRINKLER_DESIGNS,
    TENANT_PROFILES,
    get_profile,
)


def request_for(tenant_type: str, area: float = 200) -> ReviewRequest:
    profile = get_profile(tenant_type)
    return ReviewRequest(
        floor="1F",
        tenant_type_1=profile["level1"],
        tenant_type_2=tenant_type,
        area=area,
        ceiling_type="通透吊顶，通透率>70%",
    )


class SprinklerProfileTests(unittest.TestCase):
    def test_every_frontend_tenant_has_complete_sprinkler_mapping(self):
        for tenants in LEVEL1_TO_LEVEL2.values():
            for tenant in tenants:
                with self.subTest(tenant=tenant):
                    profile = TENANT_PROFILES[tenant]
                    self.assertIn("normative_sprinkler_hazard", profile)
                    self.assertIn("sprinkler_hazard", profile)
                    self.assertIn("sprinkler_design", profile)
                    self.assertEqual(
                        profile["sprinkler_hazard"],
                        profile["sprinkler_design"]["hazard"],
                    )

    def test_ordinary_retail_uses_large_mall_normative_and_project_levels(self):
        profile = get_profile("服装/鞋履/箱包/化妆品/珠宝/钟表")
        self.assertEqual("中危险级II", profile["normative_sprinkler_hazard"])
        self.assertEqual("中危险级II", profile["sprinkler_hazard"])
        self.assertEqual("8×1.3 L/(min·㎡)", profile["sprinkler_design"]["spray_intensity"])

        result = check_sprinkler(request_for("服装/鞋履/箱包/化妆品/珠宝/钟表"), profile)
        self.assertEqual("中危险级II", result.calculations["hazard_level"])
        self.assertEqual("中危险级II", result.calculations["normative_hazard_level"])
        self.assertEqual(11.5, result.calculations["max_area_per_head"])
        self.assertTrue(any("固定建筑边界下的审查分类：中危险级II" in item for item in result.details))
        self.assertTrue(any("本项目原设计采用：中危险级II" in item for item in result.details))

    def test_key_project_areas_match_design_description(self):
        expected = {
            "设备机房": ("中危险级II", "8 L/(min·㎡)", "30 L/s", "K80"),
            "小商品销售区": ("中危险级II", "16.3 L/(min·㎡)", "70 L/s", "K115"),
            "展示区": ("中危险级II", "12.2 L/(min·㎡)", "60 L/s", "K115"),
            "办公区": ("中危险级I", "6 L/(min·㎡)", "30 L/s", "K80"),
        }
        for tenant, values in expected.items():
            with self.subTest(tenant=tenant):
                design = get_profile(tenant)["sprinkler_design"]
                self.assertEqual(values, (
                    design["hazard"],
                    design["spray_intensity"],
                    design["design_flow"],
                    design["k_factor"],
                ))

    def test_warehouse_and_legacy_mixed_profile_require_manual_review(self):
        warehouse = get_profile("仓储/大件物品自提/收银折扣/卸货")
        self.assertEqual("仓库危险级II", warehouse["normative_sprinkler_hazard"])
        self.assertEqual("K363", warehouse["sprinkler_design"]["k_factor"])
        self.assertEqual("12只", warehouse["sprinkler_design"]["design_heads"])
        self.assertFalse(warehouse["auto_review"])

        legacy = get_profile("银行/美容美发/后勤/仓储/设备")
        self.assertFalse(legacy["auto_review"])
        self.assertIn("不同喷淋等级", legacy["manual_reason"])

    def test_non_tenant_project_areas_are_retained_as_design_basis(self):
        garage = PROJECT_SPRINKLER_DESIGNS["地下车库"]
        self.assertEqual("中危险级II", garage["hazard"])
        self.assertEqual("8 L/(min·㎡)", garage["spray_intensity"])

        zones = PROJECT_SPRINKLER_DESIGNS["仓储及物流区域"]["zones"]
        self.assertEqual(["100 L/s", "150 L/s", "150 L/s", "150 L/s"], [
            zone["design_flow"] for zone in zones
        ])


if __name__ == "__main__":
    unittest.main()
