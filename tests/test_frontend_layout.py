import unittest
from pathlib import Path


class FrontendLayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (Path(__file__).parents[1] / "frontend" / "index.html").read_text(
            encoding="utf-8"
        )

    def test_desktop_panels_use_dynamic_viewport_height(self):
        self.assertIn("height: calc(100dvh - 64px);", self.html)
        self.assertIn("scroll-padding-bottom: max(24px", self.html)
        self.assertIn("flex-shrink: 0;", self.html)

    def test_mobile_layout_restores_document_scrolling_and_safe_area(self):
        media = self.html.split("@media (max-width: 900px)", 1)[1]
        self.assertIn(".app-layout { grid-template-columns: 1fr; height: auto; }", media)
        self.assertIn("overflow-y: visible;", media)
        self.assertIn("env(safe-area-inset-bottom)", media)

    def test_provider_copy_is_neutral_outside_compatibility_mapping(self):
        self.assertIn("并由 AI 生成辅助意见", self.html)
        self.assertNotIn("并由 MiMo 生成辅助意见", self.html)
        self.assertEqual(self.html.count("MiMo"), 1)
        self.assertIn(
            "mimo: { badge: 'XIAOMI MIMO', title: 'MiMo AI 综合审查意见' }",
            self.html,
        )


if __name__ == "__main__":
    unittest.main()
