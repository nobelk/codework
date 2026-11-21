# Worked verification scenarios

Run each scenario in disposable repositories on both hosts. Start from [clean installs](quickstart.md), capture the model and CLI versions, record the Matt Pocock version or Git SHA, and restart the host after changing dependencies. Record what the agent actually opened, the exact prompts, outputs, gate commands and exit codes, reviewer identity, and approval or requested changes. Use a separate Codex subagent or Gemini local subagent for independent review when enabled. Otherwise give a different model the pinned, read-only packet. Keep a review pending if neither is available.

## Line Count from requirements to approval

Set `codework_checkout` to the absolute path of this checkout. Initialize a sandbox with `git init -b main`, copy [the brief](../examples/line-count/brief.md) to its root as `README.md`, and make an initial commit. Discover all eight Codework skills and the two required upstream skills in the registry.

| Stage | Codex prompt | Gemini CLI prompt | Verify |
| --- | --- | --- | --- |
| PRD | `$codework:prd Create prod_req.md from README.md.` | `Use the prd skill to create prod_req.md from README.md.` | The interview loads upstream `grilling`. The checker passes. The PRD identifies line-count and error requirements, assumptions, and the deferred multiple-file question. |
| Design | `$codework:design-doc Read prod_req.md and write docs/design/line-count.md.` | `Use the design-doc skill with prod_req.md and write docs/design/line-count.md.` | The open decisions are confirmed using `grilling`. The design maps requirement IDs to C4 views where applicable, interface contracts, tasks, and a linked ADR. Run the bundled checker and record diagram rendering. |
| Constitution | `$codework:constitution Use README.md and the design to define the initial roadmap.` | `Use the constitution skill with README.md and the design to define the initial roadmap.` | The three files under `specs/` describe scope, gate commands, and the smallest independently verifiable phase. Verify the documents remain uncommitted and independent review is recorded. |
| Spec | `$codework:spec Plan Phase 1 from specs/roadmap.md.` | `Use the spec skill to plan Phase 1 from specs/roadmap.md.` | The requirements, plan, and validation files trace the chosen phase to the PRD and ADR, order the tasks, and record the agreed command-line seam. |
| Code | `$codework:code Implement the Phase 1 spec locally and request approval.` | `Use the code skill to implement the Phase 1 spec locally and request approval.` | Upstream `tdd` is loaded. A failing test precedes each behavior change. The recorded gate commands run and the branch-local change comes back with acceptance evidence, independent review, and the exact revision for approval. |
| Refactor | `$codework:refactor Review the Phase 1 change against the initial commit, local only.` | `Use the refactor skill on the Phase 1 change against the initial commit, local only.` | Record the baseline, architecture and readability findings, confirmed plan, and independent plan review. Apply only agreed items and compare behavior and gate results. |

Use the product decisions from the brief as the test operator's interview answers. For the design, choose a single-process Python command without a dependency beyond the standard library. Confirm that text iteration handles blank lines and the final unterminated line. Accept the brief's two gates and the command-line seam when planning. Commit only approved artifacts or implementation as needed to provide a branch delta for refactor. If the refactor has no defensible item, make a separate sandbox commit that duplicates the error reporting in two branches while keeping the behavior tests green. Rerun the skill and verify the same observable exit status, standard output, and standard error after cleanup.

Input examples are an [EARS PRD](../examples/line-count/prod_req.md), a [design](../examples/line-count/design.md), and its [ADR](../examples/line-count/adr-0001.md). For the design pilot, copy those inputs into an independent sandbox and start from the design row with the example PRD. Run these checker commands from the checkout, or substitute the installed skill directories in the script paths.

```sh
python3 skills/prd/scripts/check_prd.py examples/line-count/prod_req.md
python3 skills/design-doc/scripts/check_design_doc.py examples/line-count/design.md --no-install
```

Run three negative cases in disposable copies.

1. Name a nonexistent PRD and verify the agent asks for it before drafting. Disable or remove upstream `grilling`, reopen the host, and run the pilot with the real PRD. Expect a specific dependency and install instruction, then reinstall and resume. Repeat with `tdd` and the implementation row.
2. Make a copy of the spec with a required gate that fails, or with a command absent from PATH. Verify that acceptance evidence records the exact failure and leaves the gate outstanding. Restore the real gate and rerun on the updated candidate.
3. At the first approval request, ask for a regression case with valid lines followed by an invalid UTF-8 byte. Require a nonzero exit, a diagnostic, and empty standard output. Verify that it reruns affected tests and gates, returns for independent review where affected, and asks for approval of the new revision. Record the human decision and revision together.

## Rebase with a preserved index

```sh
rebase_sandbox=$(mktemp -d)
sh "$codework_checkout/examples/rebase/setup.sh" "$rebase_sandbox"
cd "$rebase_sandbox/work"
git rev-parse HEAD origin/main
git status --short
git ls-remote origin refs/heads/feature
```

In Codex use `$codework:rebase origin/main`. In Gemini use `Use the rebase skill to replay the current branch onto origin/main.` When the conflict in `render.sh` is presented, approve `mode=main,feature`, preserving the base's new format and the feature's behavior. The first run of `sh verify.sh` fails until `feature.md` is reconciled. Check that the final report names the pinned target, conflict decision, independent review or handoff, and passing command. Compare status and content with the original, including `git show :notes.txt`, `notes.txt`, and `scratch.txt`. Compare the remote feature tip with the one above. Rerun in a new sandbox and stop at the conflict to verify the abort and restoration path.

## Review a real sandbox PR

Use a disposable GitHub repository, authenticated `gh`, and a separate reviewer account or collaborator. Push a branch that implements the line-count command and open a sandbox PR against its base. Have the reviewer leave two unresolved inline threads, one requesting an empty-file test and one requesting evidence for the final line without a newline. The maintainer runs the agent. Record the initial PR head, description, thread IDs and thread versions using `python3 <skill-dir>/scripts/pr.py fetch <pr-url>`.

1. In Codex use `$codework:review-response <pr-url> plan-only`. In Gemini use `Use the review-response skill on <pr-url> in plan-only mode.` Verify a local plan with both items, the evidence at the pinned head, proposed changes, and draft replies. Check the remote head, comments, and body for writes.
2. On the correct PR branch start the same respective skill in execute mode. Approve the code and test plan and review its verification. Ask the reviewer to edit the second comment after the snapshot but before publishing. Approve only the presented revision, exact reply text, description change, and reviewer requests.
3. Verify the remote head equals the reviewed revision and the unchanged thread received the approved reply. The edited thread is held even when the comment count is identical. Compare the reply with the actual verified test. Confirm that the PR description outside the marked block is intact and the reviewer with a held thread was excluded from reviewer requests.

The helper refreshes the head and thread state before writing. GitHub does not supply an atomic compare-and-post operation for inline replies, so preserve the observed versions and results as evidence. The local helper test exercises that contract with a GitHub CLI fixture. [GitHub pull request review comment endpoints](https://docs.github.com/en/rest/pulls/comments)
