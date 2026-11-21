import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESOURCES = {
    "prd": ("assets/template.md", "references/ears.md", "references/review.md", "scripts/check_prd.py"),
    "design-doc": (
        "assets/template.md", "references/architecture-patterns.md",
        "references/c4-mermaid.md", "references/review.md", "scripts/check_design_doc.py",
    ),
    "constitution": ("references/review.md",),
    "spec": ("references/review.md",),
    "code": ("references/trackers.md", "references/review.md"),
    "refactor": ("ARCHITECTURE.md", "CLEAN_CODE.md", "references/review.md", "scripts/pr.py"),
    "rebase": ("references/doc-sweep.md", "references/inconsistency-hunt.md", "references/review.md"),
    "review-response": ("references/review.md", "scripts/pr.py"),
}


class PackageTests(unittest.TestCase):
    def test_codex_marketplace_and_gemini_share_the_release_root(self):
        market = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text())
        self.assertEqual(market["name"], "codework")
        self.assertEqual(len(market["plugins"]), 1)
        entry = market["plugins"][0]
        self.assertEqual(entry["name"], "codework")
        self.assertEqual(entry["source"]["source"], "local")
        codex_root = (ROOT / entry["source"]["path"]).resolve()
        self.assertEqual(codex_root, ROOT)

        codex = json.loads((codex_root / "plugin.json").read_text())
        gemini = json.loads((ROOT / "gemini-extension.json").read_text())
        self.assertEqual(codex["name"], "codework")
        self.assertEqual(gemini["name"], "codework")
        self.assertRegex(codex["version"], r"^\d+\.\d+\.\d+$")
        self.assertEqual(codex["version"], gemini["version"])

    def test_skill_names_and_packaged_resources(self):
        skills = ROOT / "skills"
        entries = list(skills.rglob("SKILL.md"))
        self.assertCountEqual(entries, [skills / name / "SKILL.md" for name in RESOURCES])
        for name, required_paths in RESOURCES.items():
            with self.subTest(skill=name):
                directory = skills / name
                lines = (directory / "SKILL.md").read_text().splitlines()
                self.assertEqual(lines[0], "---")
                self.assertIn("---", lines[1:])
                header = "\n".join(lines[1:lines.index("---", 1)])
                self.assertRegex(header, rf"(?m)^name: {name}$")
                description = re.search(r"(?m)^description: (.+)$", header)
                self.assertIsNotNone(description)
                self.assertLessEqual(len(description[1]), 1024)
                if name != "code":
                    required_paths = (*required_paths, "references/workflow.md")
                for resource in required_paths:
                    self.assertTrue((directory / resource).is_file(), resource)
                for document in directory.rglob("*.md"):
                    content = document.read_text()
                    self.assertNotRegex(content, r"CLAUDE_SKILL_DIR|~/.claude|codex-companion\.mjs")
                    for path in re.findall(r"\]\(([^)#\s]+)(?:#[^)]*)?\)", content):
                        if "://" not in path and not path.startswith("mailto:"):
                            target = (document.parent / path).resolve()
                            self.assertTrue(target.is_relative_to(directory), f"{document}: {path}")
                            self.assertTrue(target.is_file(), f"{document}: {path}")

    def test_catalog_has_an_invocation_for_each_skill_on_both_hosts(self):
        catalog = (ROOT / "docs/quickstart.md").read_text()
        for name in RESOURCES:
            with self.subTest(skill=name):
                self.assertIn(f"`$codework:{name}`", catalog)
                self.assertIn(f"`Use the {name} skill`", catalog)
