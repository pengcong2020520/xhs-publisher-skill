import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "xiaohongshu-ai-publisher" / "scripts" / "normalize_note.py"


def load_module():
    spec = importlib.util.spec_from_file_location("normalize_note", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class NormalizeNoteTests(unittest.TestCase):
    def test_renumber_ordered_lists_repairs_disordered_sequence(self):
        module = load_module()
        text = "1. 第一条\n3. 第二条\n8、第三条\n\n1) 新列表\n4) 新列表第二条"

        self.assertEqual(
            module.renumber_ordered_lists(text),
            "1. 第一条\n"
            "2. 第二条\n"
            "3. 第三条\n"
            "\n"
            "1) 新列表\n"
            "2) 新列表第二条",
        )

    def test_renumber_ordered_lists_continues_across_blank_lines(self):
        module = load_module()
        text = "1. 第一条\n\n过去如此。\n\n2. 第二条\n\n现在如此。\n\n3. 第三条"

        self.assertEqual(
            module.renumber_ordered_lists(text),
            "1. 第一条\n\n过去如此。\n\n2. 第二条\n\n现在如此。\n\n3. 第三条",
        )

    def test_extract_image_placeholders_returns_five_structured_cards(self):
        module = load_module()
        text = (
            "[图1: 封面 | 核心钩子: AI红利消失]\n"
            "[图2: 问题背景 | 关键矛盾: 工具很多,问题不清]\n"
            "[图3: 核心观点 | 三个判断: 工具,流程,分发]\n"
            "[图4: 方法拆解 | 操作路径: 先写需求,再拆任务]\n"
            "[图5: 总结行动 | 建议清单: 先做工作流]"
        )

        cards = module.extract_image_placeholders(text)

        self.assertEqual([card["index"] for card in cards], [1, 2, 3, 4, 5])
        self.assertEqual(cards[0]["kind"], "封面")
        self.assertIn("AI红利消失", cards[0]["content"])
        self.assertEqual(cards[1]["kind"], "问题背景")
        self.assertEqual(cards[4]["kind"], "总结行动")

    def test_scan_light_risks_flags_absolute_income_and_unverified_claims(self):
        module = load_module()
        text = "这个方法一定能让你月入10万，业内已经证实所有人都会被AI替代。"

        risks = module.scan_light_risks(text)

        categories = {risk["category"] for risk in risks}
        self.assertIn("absolute_claim", categories)
        self.assertIn("income_promise", categories)
        self.assertIn("unsupported_claim", categories)

    def test_scan_light_risks_does_not_flag_negated_absolute_claim(self):
        module = load_module()

        risks = module.scan_light_risks("你不一定需要雇一个完整角色。")

        self.assertNotIn("absolute_claim", {risk["category"] for risk in risks})


if __name__ == "__main__":
    unittest.main()
