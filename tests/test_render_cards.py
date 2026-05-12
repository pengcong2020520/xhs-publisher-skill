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
    def test_build_cards_from_placeholders_returns_five_card_models(self):
        module = load_module()
        cards = module.build_cards_from_placeholders(
            [
                {"index": 1, "kind": "封面", "content": "核心钩子: AI红利消失"},
                {"index": 2, "kind": "问题背景", "content": "关键矛盾: 工具很多,问题不清"},
                {"index": 3, "kind": "核心观点", "content": "三个判断: 工具,流程,分发"},
                {"index": 4, "kind": "方法拆解", "content": "操作路径: 先写需求,再拆任务"},
                {"index": 5, "kind": "总结行动", "content": "建议清单: 先做工作流"},
            ],
            title="普通人别再追AI工具了",
        )

        self.assertEqual(
            [card["filename"] for card in cards],
            ["card-01.html", "card-02.html", "card-03.html", "card-04.html", "card-05.html"],
        )
        self.assertEqual(cards[0]["headline"], "普通人别再追AI工具了")
        self.assertEqual(cards[1]["headline"], "问题背景")
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
            self.assertIn("xiaohongshu-card", html)
            self.assertIn("观点洞察", html)

    def test_prepare_screenshot_html_scales_card_for_hidpi_output(self):
        module = load_module()
        source = "<html><head><style>.card-shell { color: #111; }</style></head><body></body></html>"

        scaled = module.prepare_screenshot_html(source, 2)

        self.assertIn("transform: scale(2);", scaled)
        self.assertIn("2484px", scaled)
        self.assertIn("3312px", scaled)

    def test_split_card_points_parses_semicolon_content(self):
        module = load_module()

        points = module.split_card_points("三个判断: 不是代码不重要了;不是程序员没有价值了;不是人人都要学编程")

        self.assertEqual(
            points,
            ["不是代码不重要了", "不是程序员没有价值了", "不是人人都要学编程"],
        )

    def test_split_card_points_turns_clauses_into_independent_points(self):
        module = load_module()

        points = module.split_card_points("三个判断: 代码会越来越便宜，定义问题会越来越贵，会调用 Skill 的人更吃香")

        self.assertEqual(
            points,
            ["代码会越来越便宜", "定义问题会越来越贵", "会调用 Skill 的人更吃香"],
        )

    def test_render_card_html_does_not_repeat_long_clause_as_hook(self):
        module = load_module()

        html = module.render_card_html(
            {
                "filename": "card-01.html",
                "kind": "封面",
                "headline": "Vibe Coding 真正改变的不是程序员",
                "body": "核心钩子: 不是程序员消失了;是普通人也能调用编程能力",
            }
        )

        self.assertNotIn("不是程序员消失了;是普通人也能调用编程能力", html)
        self.assertIn("不是程序员消失了", html)
        self.assertIn("是普通人也能调用编程能力", html)

    def test_build_hook_supports_five_page_story_arc(self):
        module = load_module()

        self.assertEqual(
            module.build_hook({"kind": "问题背景", "body": ""}, ["工具越来越多", "判断越来越难"]),
            "先把矛盾讲清楚",
        )
        self.assertEqual(
            module.build_hook({"kind": "方法拆解", "body": ""}, ["先写需求", "再拆任务"]),
            "照这个路径执行",
        )
        self.assertEqual(
            module.build_hook({"kind": "案例启发", "body": ""}, ["一个真实场景", "一条复用经验"]),
            "把经验变成模板",
        )


if __name__ == "__main__":
    unittest.main()
