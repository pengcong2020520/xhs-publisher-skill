import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "xiaohongshu-ai-publisher" / "scripts" / "publish_note.py"


def load_module():
    spec = importlib.util.spec_from_file_location("publish_note", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PublishNoteTests(unittest.TestCase):
    def test_build_post_command_includes_title_body_and_images(self):
        module = load_module()
        command = module.build_post_command("标题", "正文", ["a.png", "b.png"])

        self.assertEqual(
            command,
            ["xhs", "post", "--title", "标题", "--body", "正文", "--images", "a.png", "b.png"],
        )

    def test_validate_images_rejects_missing_files_and_non_images(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            image = directory / "card.png"
            note = directory / "note.txt"
            image.write_bytes(b"fake")
            note.write_text("not an image", encoding="utf-8")

            errors = module.validate_images([str(image), str(note), str(directory / "missing.png")])

        self.assertEqual(len(errors), 2)
        self.assertIn("not a supported image", errors[0])
        self.assertIn("does not exist", errors[1])

    def test_diagnose_failure_classifies_common_cli_errors(self):
        module = load_module()

        self.assertEqual(module.diagnose_failure("command not found: xhs"), "cli_missing")
        self.assertEqual(module.diagnose_failure("请先登录 or cookies expired"), "auth_required")
        self.assertEqual(module.diagnose_failure("No such file or directory: card.png"), "missing_image")
        self.assertEqual(module.diagnose_failure("HTTP 429 too many requests"), "rate_limited")


if __name__ == "__main__":
    unittest.main()
