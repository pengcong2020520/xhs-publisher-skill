import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "xiaohongshu-ai-publisher" / "scripts" / "render_cards.py"


def load_module():
    spec = importlib.util.spec_from_file_location("render_cards", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RenderCardsTests(unittest.TestCase):
    def test_build_cards_from_placeholders_returns_three_card_models(self):
        module = load_module()
        cards = module.build_cards_from_placeholders(
            [
                {"index": 1, "kind": "封面", "content": "核心钩子: AI红利消失"},
                {"index": 2, "kind": "核心观点", "content": "三个判断: 工具,流程,分发"},
                {"index": 3, "kind": "总结行动", "content": "建议清单: 先做工作流"},
            ],
            title="普通人别再追AI工具了",
        )

        self.assertEqual([card["filename"] for card in cards], ["card-01.html", "card-02.html", "card-03.html"])
        self.assertEqual(cards[0]["headline"], "普通人别再追AI工具了")
        self.assertIn("AI红利消失", cards[0]["body"])

    def test_write_card_html_outputs_responsive_html_files(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            cards = [
                {
                    "filename": "card-01.html",
                    "kind": "封面",
                    "headline": "普通人别再追AI工具了",
                    "body": "核心钩子: AI红利消失",
                }
            ]

            paths = module.write_card_html(cards, output_dir)

            self.assertEqual(paths, [output_dir / "card-01.html"])
            html = paths[0].read_text(encoding="utf-8")
            self.assertIn("普通人别再追AI工具了", html)
            self.assertIn("1242", html)
            self.assertIn("card-shell", html)

    def test_prepare_screenshot_html_scales_card_for_hidpi_output(self):
        module = load_module()
        source = "<html><head><style>.card-shell { color: #111; }</style></head><body></body></html>"

        scaled = module.prepare_screenshot_html(source, 2)

        self.assertIn("transform: scale(2);", scaled)
        self.assertIn("2484px", scaled)
        self.assertIn("3312px", scaled)


if __name__ == "__main__":
    unittest.main()
