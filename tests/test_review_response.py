import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "skills/review-response/scripts/pr.py"
REFACTOR_HELPER = ROOT / "skills/refactor/scripts/pr.py"
PR_URL = "https://github.com/example/project/pull/7"
HEAD = "b" * 40
ROOT_COMMENT_ID = 3_000_000_011


class ReviewResponseTests(unittest.TestCase):
    def setUp(self):
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.directory = Path(scratch.name)
        self.state_path = self.directory / "state.json"
        self.state = {
            "pr": {"head": HEAD, "body": "Maintainer's introduction", "state": "OPEN"},
            "thread": {
                "id": "thread-1", "path": "line_count.py", "line": 5, "originalLine": 5,
                "startLine": None, "isResolved": False, "isOutdated": False, "resolvedBy": None,
                "comments": {"totalCount": 1, "nodes": [{
                    "fullDatabaseId": str(ROOT_COMMENT_ID), "author": {"login": "reviewer"},
                    "body": "How is a blank line counted?",
                    "createdAt": "2026-11-21T12:00:00Z", "updatedAt": "2026-11-21T12:00:00Z",
                    "url": f"{PR_URL}#discussion_r{ROOT_COMMENT_ID}", "diffHunk": "@@ -1 +1 @@",
                }]},
            },
        }
        self.save_state()

    def save_state(self):
        self.state_path.write_text(json.dumps(self.state))

    def run_helper(self, command, *args, succeeds=True, helper=HELPER):
        env = os.environ | {
            "PATH": str(ROOT / "tests/fixtures") + os.pathsep + os.environ["PATH"],
            "CODEWORK_GH_STATE": str(self.state_path),
        }
        result = subprocess.run(
            [sys.executable, str(helper), command, PR_URL, *map(str, args)],
            capture_output=True, text=True, env=env, timeout=10,
        )
        if succeeds:
            self.assertEqual(result.returncode, 0, result.stderr)
            return json.loads(result.stdout)
        self.assertNotEqual(result.returncode, 0)
        return result.stderr

    def prepare_reply(self):
        snapshot = self.run_helper("fetch")
        replies_file = self.directory / "replies.json"
        body = "I added a blank-line test in bbbbbbb."
        replies_file.write_text(json.dumps([{
            "reply_to": ROOT_COMMENT_ID, "seen_thread_version": snapshot["threads"][0]["thread_version"],
            "body": body,
        }]))
        return replies_file, body

    def test_plan_only_and_approved_reply_on_the_expected_head(self):
        replies, body = self.prepare_reply()
        dry_run = self.run_helper("reply", replies, "--dry-run")
        self.assertEqual(dry_run["would_post"], [{"target": ROOT_COMMENT_ID}])
        self.assertEqual(json.loads(self.state_path.read_text()), self.state)

        sent = self.run_helper("reply", replies, "--expect-head", HEAD)
        self.assertEqual(sent["posted"], [{"target": ROOT_COMMENT_ID, "url": f"{PR_URL}#discussion_r22"}])
        self.assertEqual(self.run_helper("fetch")["threads"][0]["comments"][-1]["body"], body)
        retried = self.run_helper("reply", replies, "--expect-head", HEAD)
        self.assertEqual(len(retried["skipped"]), 1)

    def test_thread_edit_at_the_same_comment_count_holds_reply(self):
        replies, _ = self.prepare_reply()
        comment = self.state["thread"]["comments"]["nodes"][0]
        comment["body"] = "Please count two newlines as two blank lines."
        comment["updatedAt"] = "2026-11-21T12:05:00Z"
        self.save_state()

        outcome = self.run_helper("reply", replies, "--expect-head", HEAD)

        self.assertEqual(outcome["posted"], [])
        self.assertEqual([item["target"] for item in outcome["held"]], [ROOT_COMMENT_ID])
        self.assertEqual(json.loads(self.state_path.read_text()), self.state)

    def test_deleted_thread_holds_reply(self):
        replies, _ = self.prepare_reply()
        self.state["thread"] = None
        self.save_state()

        outcome = self.run_helper("reply", replies, "--expect-head", HEAD)

        self.assertEqual(outcome["posted"], [])
        self.assertEqual([item["target"] for item in outcome["held"]], [ROOT_COMMENT_ID])

    def test_invalid_batch_stops_before_posting_valid_earlier_item(self):
        replies, _ = self.prepare_reply()
        items = json.loads(replies.read_text())
        items.append({"conversation": True, "body": 123})
        replies.write_text(json.dumps(items))

        self.assertIn("body", self.run_helper("reply", replies, "--expect-head", HEAD, succeeds=False))
        self.assertEqual(json.loads(self.state_path.read_text()), self.state)

    def test_conversation_refresh_deduplicates_comment_added_during_batch(self):
        replies, _ = self.prepare_reply()
        summary = "I verified the final line."
        comment_url = f"{PR_URL}#issuecomment-99"
        items = json.loads(replies.read_text())
        items.append({"conversation": True, "body": summary})
        replies.write_text(json.dumps(items))
        self.state["conversation_after_reply"] = {
            "id": 99, "user": {"login": "engineer"}, "body": summary, "html_url": comment_url,
        }
        self.save_state()

        result = self.run_helper("reply", replies, "--expect-head", HEAD)

        self.assertEqual(len(result["posted"]), 1)
        self.assertEqual(result["skipped"], [{
            "target": "conversation", "reason": "already posted", "url": comment_url,
        }])

    def test_pr_head_must_still_match_before_writes(self):
        replies, _ = self.prepare_reply()
        self.state["pr"]["head"] = "c" * 40
        self.save_state()
        section = self.directory / "pr-section.md"
        section.write_text("Changes verified.")

        self.assertIn("head", self.run_helper("reply", replies, "--expect-head", HEAD, succeeds=False))
        self.assertIn("head", self.run_helper("body", section, "--expect-head", HEAD, succeeds=False))
        self.assertEqual(json.loads(self.state_path.read_text()), self.state)
        result = self.run_helper("body", section, "--expect-head", "c" * 40)
        self.assertTrue(result["changed"])
        updated = json.loads(self.state_path.read_text())["pr"]["body"]
        self.assertIn("Maintainer's introduction", updated)
        self.assertIn("Changes verified.", updated)
        self.assertFalse(self.run_helper("body", section, "--expect-head", "c" * 40)["changed"])

    def test_pr_body_helpers_refuse_unmatched_markers_without_a_write(self):
        section = self.directory / "pr-section.md"
        section.write_text("Changes verified.")
        for skill, helper, args in (
            ("review-response", HELPER, ("--expect-head", HEAD)),
            ("refactor", REFACTOR_HELPER, ()),
        ):
            with self.subTest(skill=skill):
                self.state["pr"]["body"] = f"<!-- {skill}:start -->\nMaintainer's notes"
                self.save_state()
                error = self.run_helper("body", section, *args, succeeds=False, helper=helper)
                self.assertIn("invalid managed block markers", error)
                self.assertEqual(json.loads(self.state_path.read_text()), self.state)
