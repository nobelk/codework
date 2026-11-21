---
name: rebase
description: Replay the current branch onto a pinned base, confirm risky conflict resolutions, reconcile code and documentation, verify gates, and restore uncommitted work locally.
license: Apache-2.0
---

# rebase

Read the [rebase workflow](references/workflow.md) before changing any Git state. Replay only the current branch onto the exact resolved target commit. Record the old tip, fork point, and target SHA before replay, and preserve the index, worktree, and untracked content.

Resolve mechanical conflicts with evidence from both sides. Obtain the user's decision before staging any risky resolution or dropping a commit. Track conflict decisions and verify the replay. Use the [inconsistency hunt](references/inconsistency-hunt.md) and [documentation sweep](references/doc-sweep.md) to reconcile code, tests, and docs with the new base.

Obtain [independent review](references/review.md) or prepare a pending handoff, then run the repository gates on the rebased revision. Restore and verify preserved local work on completion or abort, even if verification fails. Report the new tip, gates, review, and restored work or backup locations. Leave publication to the engineer.
