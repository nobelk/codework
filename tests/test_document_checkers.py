import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples/line-count"


class DocumentCheckerTests(unittest.TestCase):
    def checker(self, skill, script, document, *flags):
        return subprocess.run(
            [sys.executable, str(ROOT / "skills" / skill / "scripts" / script),
             str(EXAMPLE / document), *flags],
            capture_output=True, text=True, timeout=15,
        )

    def test_example_prd_passes_ears_and_trace_checks(self):
        result = self.checker("prd", "check_prd.py", "prod_req.md")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("result: PASS", result.stdout)

    def test_prd_rejects_empty_requirement_tables(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "empty-requirements.md"
            lines = (EXAMPLE / "prod_req.md").read_text().splitlines()
            path.write_text("\n".join(line for line in lines if not line.startswith(("| FR", "| NFR"))))
            result = self.checker("prd", "check_prd.py", path)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("section 6 has no FR items", result.stdout)
        self.assertIn("section 7 has no NFR items", result.stdout)

    def test_design_reports_structure_separately_from_rendering(self):
        result = self.checker("design-doc", "check_design_doc.py", "design.md", "--no-render")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("2 captioned and cited", result.stdout)
        self.assertIn("result: UNVERIFIED DIAGRAMS", result.stdout)

    def test_design_checker_rejects_missing_input(self):
        result = self.checker("design-doc", "check_design_doc.py", "missing.md", "--no-install")
        self.assertEqual(result.returncode, 1)
        self.assertIn("cannot read the document", result.stdout)

    def test_design_checker_rejects_an_unterminated_mermaid_block(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "unclosed-diagram.md"
            path.write_text((EXAMPLE / "design.md").read_text() + "\n```mermaid\nflowchart TD\n")
            result = self.checker("design-doc", "check_design_doc.py", path, "--no-render")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("unterminated Mermaid block", result.stdout)
