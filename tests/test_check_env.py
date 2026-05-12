import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "xiaohongshu-ai-publisher" / "scripts" / "check_env.py"


def load_module():
    spec = importlib.util.spec_from_file_location("check_env", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CheckEnvTests(unittest.TestCase):
    def test_classify_status_failure_detects_config_permission_issue(self):
        module = load_module()

        self.assertEqual(
            module.classify_status_failure("PermissionError: Operation not permitted: '/Users/me/.xiaohongshu-cli'"),
            "config_permission",
        )

    def test_classify_status_failure_detects_auth_required(self):
        module = load_module()

        self.assertEqual(module.classify_status_failure("cookies expired, please login"), "auth_required")


if __name__ == "__main__":
    unittest.main()
