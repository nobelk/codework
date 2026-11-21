import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class RebaseScenarioTests(unittest.TestCase):
    def setUp(self):
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.sandbox = Path(scratch.name)
        self.work = self.sandbox / "work"
        self.env = os.environ | {"GIT_EDITOR": "true", "GIT_CONFIG_NOSYSTEM": "1",
                                 "GIT_CONFIG_GLOBAL": os.devnull}
        subprocess.run(
            ["sh", str(ROOT / "examples/rebase/setup.sh"), scratch.name],
            env=self.env, check=True, capture_output=True, timeout=15,
        )
        self.original_head = self.git("rev-parse", "HEAD").stdout.strip()
        self.original_status = self.git("status", "--porcelain").stdout
        self.original_remote_tip = self.git("ls-remote", "origin", "refs/heads/feature").stdout
        self.pinned_base = self.git("rev-parse", "origin/main").stdout.strip()

    def git(self, *args, check=True):
        return subprocess.run(
            ["git", *args], cwd=self.work, env=self.env, capture_output=True,
            text=True, check=check, timeout=15,
        )

    def begin_conflicting_rebase(self):
        self.git("stash", "push", "--all", "-m", "rebase feature")
        stash_oid = self.git("rev-parse", "refs/stash").stdout.strip()
        result = self.git("rebase", "--no-autostash", "--no-update-refs", self.pinned_base, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.git("diff", "--name-only", "--diff-filter=U").stdout, "render.sh\n")
        return stash_oid

    def restore_and_check(self, stash_oid):
        self.git("stash", "apply", "--index", stash_oid)
        self.assertEqual(self.git("status", "--porcelain").stdout, self.original_status)
        self.assertEqual(self.git("show", ":notes.txt").stdout, "original\nstaged\n")
        self.assertEqual((self.work / "notes.txt").read_text(), "original\nstaged\nunstaged\n")
        self.assertEqual((self.work / "scratch.txt").read_text(), "untracked\n")
        self.assertEqual((self.work / "cache.local").read_text(), "ignored\n")
        self.assertEqual(
            self.git("ls-remote", "origin", "refs/heads/feature").stdout, self.original_remote_tip
        )

    def test_replay_reconcile_verify_and_restore_without_pushing(self):
        stash_oid = self.begin_conflicting_rebase()
        (self.work / "render.sh").write_text('printf "mode=main,feature\\n"\n')
        self.git("add", "--", "render.sh")
        self.git("rebase", "--continue")
        self.git("merge-base", "--is-ancestor", self.pinned_base, "HEAD")

        gate = ["sh", "verify.sh"]
        self.assertNotEqual(subprocess.run(gate, cwd=self.work, timeout=10).returncode, 0)
        (self.work / "feature.md").write_text("mode=main,feature\n")
        self.git("add", "--", "feature.md")
        self.git("commit", "-qm", "Reconcile the feature example with the new base")
        subprocess.run(gate, cwd=self.work, check=True, timeout=10)
        self.restore_and_check(stash_oid)

    def test_abort_restores_index_worktree_and_untracked_file(self):
        stash_oid = self.begin_conflicting_rebase()
        self.git("rebase", "--abort")
        self.assertEqual(self.git("rev-parse", "HEAD").stdout.strip(), self.original_head)
        self.restore_and_check(stash_oid)

    def test_ignored_files_survive_tracked_file_directory_collisions(self):
        incoming = self.sandbox / "incoming"
        self.git("worktree", "add", str(incoming), "main")
        (incoming / "collision-file").mkdir()
        (incoming / "collision-file/base.txt").write_text("upstream directory\n")
        (incoming / "collision-directory").write_text("upstream file\n")
        self.git("-C", str(incoming), "add", "-f", "--", "collision-file/base.txt", "collision-directory")
        self.git("-C", str(incoming), "commit", "-qm", "Track new paths")
        self.pinned_base = self.git("rev-parse", "main").stdout.strip()
        (self.work / "collision-file").write_text("local file\n")
        (self.work / "collision-directory").mkdir()
        (self.work / "collision-directory/local.txt").write_text("local directory\n")

        stash_oid = self.begin_conflicting_rebase()
        (self.work / "render.sh").write_text('printf "mode=main,feature\\n"\n')
        self.git("add", "--", "render.sh")
        self.git("rebase", "--continue")

        self.assertEqual((self.work / "collision-file/base.txt").read_text(), "upstream directory\n")
        self.assertEqual((self.work / "collision-directory").read_text(), "upstream file\n")
        self.assertEqual(self.git("show", f"{stash_oid}^3:collision-file").stdout, "local file\n")
        self.assertEqual(
            self.git("show", f"{stash_oid}^3:collision-directory/local.txt").stdout,
            "local directory\n",
        )
