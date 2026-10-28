import tempfile, unittest
from pathlib import Path
from ripplemap.analyzer import scan_repository

class AnalyzerTests(unittest.TestCase):
    def test_impact_and_candidate_test(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "app").mkdir(); (root / "tests").mkdir()
            (root / "app" / "__init__.py").write_text("", encoding="utf-8")
            (root / "app" / "service.py").write_text("def run():\n    return 1\n", encoding="utf-8")
            (root / "app" / "routes.py").write_text("from app.service import run\n", encoding="utf-8")
            (root / "app" / "main.py").write_text("from app.routes import run\n", encoding="utf-8")
            (root / "tests" / "test_service.py").write_text("from app.service import run\n", encoding="utf-8")
            report = scan_repository(root, "app/service.py")
            impacted = {x["file"]: x["distance"] for x in report["impacted_files"]}
            self.assertEqual(impacted["app/routes.py"], 1)
            self.assertEqual(impacted["app/main.py"], 2)
            self.assertIn("tests/test_service.py", [x["file"] for x in report["candidate_tests"]])

    def test_relative_import(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); (root / "pkg").mkdir()
            (root / "pkg" / "__init__.py").write_text("", encoding="utf-8")
            (root / "pkg" / "helper.py").write_text("VALUE = 1\n", encoding="utf-8")
            (root / "pkg" / "consumer.py").write_text("from .helper import VALUE\n", encoding="utf-8")
            report = scan_repository(root, "pkg/helper.py")
            self.assertEqual(report["direct_dependents"], ["pkg/consumer.py"])

    def test_outside_changed_file_rejected(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            inside = Path(a) / "inside.py"; inside.write_text("x=1\n", encoding="utf-8")
            outside = Path(b) / "outside.py"; outside.write_text("x=2\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                scan_repository(a, outside)

if __name__ == "__main__":
    unittest.main()
