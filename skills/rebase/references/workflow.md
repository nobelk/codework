Paths written as `<skill-dir>` resolve from the folder containing the activated SKILL.md.

# Rebase skill

Bring `<input>`'s changes into the **current** branch by replaying the current branch's commits on top of `<input>`'s tip. `<input>` is only ever read, and no other branch moves. A clean replay is not the finish line: the rebase resolves *textual* overlap only, so the branch's own code, tests, and docs then have to be made consistent with what `<input>` changed underneath them.

Output: linear history on the current branch, every conflict and reconciliation edit accounted for, a documentation staleness sweep, an adjudicated independent review, green gates, and the user's uncommitted work back where it was.

The repo's repository guidance and `AGENTS.md` govern every edit made here; read `AGENTS.md` if it isn't already in context. The skill never pushes: publishing a rewritten branch is the user's call.

Use the primary session for all Git mutations and decisions. Once local changes have been stashed, finish or abort an active rebase before restoring them. Run Step 6 on every exit after stashing, including failed checks.

## Step 0 - Preflight

Stop before touching anything rather than partway through.

1. **Resolve `<input>`** from the argument to a full refname, `refs/heads/<name>` or `refs/remotes/<remote>/<name>`, and use that from here on: a tag or other ref with the same short name otherwise wins silently. With no argument, list `git branch -a --sort=-committerdate` and ask the user to pick, offering the default branch's remote ref (e.g. `origin/main`) first. If the user named a branch to rebase that isn't the current one, ask before checking it out. If `<input>` exists neither locally nor on any remote, tell the user and stop.
   - **Remote ref** (`origin/main`, or a name that exists only on a remote): fetch with an explicit refspec, `git fetch <remote> '+refs/heads/<name>:refs/remotes/<remote>/<name>'`, then `git rev-parse --verify refs/remotes/<remote>/<name>`. A plain `git fetch <remote> <name>` can update only `FETCH_HEAD` in a single-branch or narrowed clone, leaving the tracking ref stale while reporting success. Rebase onto the tracking ref directly; no local branch is needed.
   - **Local branch:** get the full tracking ref with `git for-each-ref --format='%(upstream)' <input>`. If it names a remote ref, fetch it as above. If `git rev-list <input>..<upstream-ref>` returns commits, ask whether to rebase onto the local tip, the upstream tip, or stop.
2. **Check there is something to do.** Record `git branch --show-current` as `<current>`. Stop and tell the user when:
   - `<current>` is empty: a detached HEAD, which is also what a rebase in progress looks like;
   - a merge, cherry-pick, or revert is in progress (`MERGE_HEAD`, `CHERRY_PICK_HEAD`, `REVERT_HEAD`, `rebase-merge`, or `rebase-apply` exists at `git rev-parse --git-path <name>`), since stashing would silently cancel it;
   - `git merge-base --is-ancestor <input> HEAD` succeeds: `<input>` is already in the branch.
3. **Record the fixed points** and echo them in the conversation, so they survive an interrupted session:
   ```bash
   git rev-parse HEAD             # <pre-rebase-sha>: the rollback point
   git rev-parse <input>          # <input-sha>: the new base, and the review base in Step 4
   git merge-base HEAD <input>    # <fork-point>: where the branch left <input>'s history
   ```
   From here on use `<input-sha>`, not the ref, so a fetch mid-run cannot move the base.
4. **Clear the working tree.**
   - Look in `git stash list` for an entry named `rebase <current>`: an interrupted earlier run left it there. Tell the user about it before going on.
   - Use `git status --porcelain --untracked-files=all --ignored=matching` to detect staged, unstaged, untracked, and ignored files. Record the ignored paths separately with `git ls-files --others --ignored --exclude-standard -z`. Record the current `refs/stash` if present, then run `git stash push --all -m "rebase <current>"` when the status is nonempty. Record the new `refs/stash` value as `<stash-oid>`. Including ignored files protects them when a base or replayed commit starts tracking their paths or replaces a directory with a file.
   - Confirm that Git created the expected stash and cleared the tree. Stop if local work is still present, for example in a dirty submodule or nested repository. If a stash was created, run Step 6 before reporting. Keep the stash until verification and restoration are complete.

## Step 1 - Survey both sides

Do this in the main loop: Step 2's conflicts are resolved here, so both sides' intent has to be in this context, not a subagent's.

```bash
git log --format='%h %s%n%b' <fork-point>..<pre-rebase-sha>         # the branch's own commits: these get replayed
git rev-list --count <fork-point>..<input-sha>                       # how far behind the branch is
comm -12 <(git diff --name-only <fork-point> <pre-rebase-sha> | sort) \
         <(git diff --name-only <fork-point> <input-sha> | sort)     # <overlap>: files both sides touched
git log --format='%h %s%n%b' <fork-point>..<input-sha> -- <overlap>  # incoming intent where the sides collide
```

The overlap is where conflicts and semantic inconsistencies will be. Read both sides' diffs of those files now; on a large overlap, read each file's two diffs when its conflict comes up instead. If several of the branch's commits touch the same overlapping file, the same conflict will recur as each one is replayed: resolve it the same way each time.

Check two things about the branch's own commits before replaying them:

- **Commits that aren't the branch's own.** If the branch was stacked on another branch that has since been squash-merged into `<input>`, the parent's commits are still in `<fork-point>..<pre-rebase-sha>` and would be replayed against their own squash. Ask the user for the true fork point, set `<fork-point>` to it, and use the `--onto` form in Step 2.
- **Merge commits.** The rebase flattens them: the commits they brought in that `<input>` lacks are replayed, but whatever a merge itself changed (a conflict resolution, a manual fix-up) is not, and range-diff won't show the loss. For each of `git rev-list --merges <fork-point>..<pre-rebase-sha>`, keep the output of `git show --remerge-diff <merge>` when it is non-empty; Step 2 checks those changes survived.

## Step 2 - Rebase

```bash
git rebase --no-autostash --no-update-refs --no-rebase-merges --no-rerere-autoupdate <input-sha>
git rebase --no-autostash --no-update-refs --no-rebase-merges --no-rerere-autoupdate --onto <input-sha> <fork-point>
```

Use the `--onto` form when Step 1 moved `<fork-point>`. `--no-update-refs` keeps other local branches where they are. `--no-rebase-merges` applies the flattening described in Step 1. `--no-rerere-autoupdate` leaves cached conflict resolutions unstaged for inspection and approval.

Resolve conflicts yourself, and confirm the risky ones. Record every conflict in a **conflict list** (replayed commit, file, mechanical or risky, resolution); Steps 3, 4, and 7 use it.

- **Mechanical** (one side moved or reformatted code the other edited, import lists, adjacent additions, lockfiles): resolve directly, preserving both intents.
- **Risky** (both sides made meaningful, incompatible changes to the same logic, API signature, test expectation, or doc statement): show the user both sides and your recommendation and obtain their explicit decision before staging it. Offer concrete resolutions ("keep the branch's signature, port the input's body"; "take the input's version, re-apply the branch's fix on top"), not "ours/theirs".
- Then `git add` the resolved files and `git rebase --continue`.
- `git rebase --skip` drops that commit's changes entirely, so ask before using it.
- If the rebase becomes unrecoverable, or the user stops at a question, `git rebase --abort` returns the branch to `<pre-rebase-sha>` untouched; run Step 6, report, and stop.

When the rebase finishes, check it:

```bash
git merge-base --is-ancestor <input-sha> HEAD                        # must succeed
git range-diff <fork-point>..<pre-rebase-sha> <input-sha>..HEAD
comm -23 <(git diff --name-only <pre-rebase-sha> HEAD | sort) \
         <(git diff --name-only <fork-point> <input-sha> | sort)     # must be empty
```

- **Range-diff.** `=` is a commit replayed unchanged and `!` one that changed. A `!` whose inner diff touches only context lines comes from `<input>` editing nearby code and is expected; one that changes `+`/`-` lines should trace to the conflict list. A `<` with no matching `>` is a commit that no longer exists: git drops a commit whose change is already upstream or that became empty, and a heavily resolved commit can also show as an unmatched `<`/`>` pair. List each dropped commit for the report, and raise any you can't explain with the user.
- **Path check.** The last command lists paths that changed across the rebase although `<input>` never touched them: content the replay lost or altered. Together with the merge changes kept in Step 1 (conflict resolutions are usually redone during the replay; manual fix-ups are not), restore whatever is missing in a reconciliation commit, asking when it isn't clear what the branch meant.

If HEAD is now `<input-sha>`, every commit was already upstream and there is nothing to reconcile or review: run Step 6 and report.

## Step 3 - Reconcile with the incoming changes

Now find the **semantic** inconsistencies: places where the branch's own work no longer agrees with what `<input>` changed under it. Run this step even when the rebase had no conflicts.

Use separate read-only readers when available, or perform the two sweeps directly. Give readers the repo path, `<fork-point>`, `<pre-rebase-sha>`, `<input-sha>`, the conflict list, and the absolute path of its procedure in this skill's `references/` directory:

- **Inconsistency hunt** (`references/inconsistency-hunt.md`): stale calls, tests encoding behavior the other side changed, rules one side added that the other breaks, duplicated work, and conflict resolutions that dropped one side's intent.
- **Doc sweep** (`references/doc-sweep.md`): docs, specs, and ADRs the rebase made stale.

Check each returned site against the tree, then fix the ones that hold as minimal edits in the main loop, following the repo's conventions (tests updated alongside behavior, doc style matched). Ask the user about every `needs user decision` they return, and whenever a fix means choosing between the two sides' designs.

Commit the edits on top as one or a few labeled commits (e.g. `Reconcile <area> with <input> changes`), staging by explicit path and following the repo's commit convention. Leave the replayed commits as they are, so the reconciliation stays reviewable on its own.

## Step 4 - Independent review

Use [the review instructions](review.md) to review the replayed and reconciled delta against the pinned base. Adjudicate findings and commit accepted fixes before the final gate run. If review is pending, keep that status in the handoff and proceed with local checks and restoration.

## Step 5 - Gates

Run the exact commands from `specs/tech-stack.md` and the repository for format, lint, build or typecheck, and the full test suite. Bound each command's runtime and record the command, checked revision, and outcome.

- If a stash exists, run the gates in a temporary detached worktree at the candidate SHA. Safely provision required ignored inputs there from the original recorded paths, using the stash or the project's setup, without replacing any tracked paths. This keeps generated outputs out of the worktree where the stash will be restored. Record a gate as unavailable if a needed input cannot be restored or provisioned. If the gates require a fix, apply it to the rebased branch, commit, and rerun on the new candidate.

- **A failure that traces to a resolution or reconciliation edit:** fix forward, commit, and re-run.
- **A failure that looks pre-existing:** run the failing command at `<input-sha>` and at `<pre-rebase-sha>` in throwaway worktrees (`git worktree add --detach <tmp> <sha>`, plus `git submodule update --init` if the repo has submodules; afterwards `git worktree remove --force <tmp>` and `git worktree prune`). If either is red, the failure came with that side: ask whether to fix it here or hand off with it documented. If both are green, the rebase caused it: fix forward. A fresh worktree lacks ignored local config such as `.env`; if the failure could come from that, say the baseline is unreliable rather than calling it pre-existing.
- Record passed, failed, unavailable, or inapplicable, with a reason for any unverified gate.

## Step 6 - Restore the stashed work

If Step 0 created a stash, restore it as follows.

1. Leave only the verified branch changes committed and preserve unrelated changes. Find the stash by object ID using `git stash list --format='%gd %H'`.
2. Identify untracked and ignored stash paths in `<stash-oid>^3` that match or are ancestors or descendants of tracked paths. Preserve these files in a fresh scratch directory before restoration. If the new base occupies an original path, present the backup location and ask where to restore it.
3. Run `git stash apply --index <stash-oid>`. If it fails, inspect the index and worktree first. Retry without `--index` only if the failed apply left both untouched and the user agrees to restore staging separately. When it partially applied, reconcile what is already present before restoring any missing paths. Preserve files at spare paths when the new base occupies their original paths. Confirm risky choices with the user.
4. Compare restored staged, unstaged, untracked, and ignored work with the stash and report staging or path differences. Drop the entry only after verifying its contents are recoverable in the worktree or backups. If recovery is incomplete, retain the stash and give the user its ID and the remaining work.

## Step 7 - Report

Follow the repo's handoff checklist if it has one. On an early stop, report the same way: what ran, and the state the branch was left in. Cover:

- **What landed:** `<input>` and `<input-sha>`; how many commits were replayed and which were dropped (from the range-diff); `<pre-rebase-sha>` and the new tip; and the rollback, `git reset --hard <pre-rebase-sha>`. Set any restored uncommitted work aside before rolling back, since `--hard` discards it.
- **Publishing:** report the local tip and leave any push to the engineer.
- **Conflicts:** each entry of the conflict list, and any content the path check restored.
- **Reconciliation:** each edit, mapped to the inconsistency it fixed, and the build/typecheck result.
- **Doc sweep:** the candidate documents checked, each stale statement fixed, and any left standing with the reason. When nothing was stale, say so: "no docs were stale" is a finding; "docs were not checked" is a gap.
- **Independent review:** accept / reject / defer counts, a one-line reason for each rejection, and reviewer and revision, or the pending handoff.
- **Gates:** each gate, its command, and its state.
- **Stash:** restored cleanly, or what went differently (staging lost, conflicts resolved, files written as `.stashed`). The restored work was not part of the reconciliation, review, or gates. If any of it couldn't be restored, give `<stash-oid>` and the command to recover it, `git stash apply <stash-oid>`.
- **Remaining risk:** deferred findings, and interactions the gates can't cover.
