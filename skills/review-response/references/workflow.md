Paths written as `<skill-dir>` resolve from the folder containing the activated SKILL.md.

# Review-response skill

Act as a principal engineer answering the review on a pull request. The flow:

snapshot the PR → gather evidence per item → classify and draft replies → **grill** the user on the contested calls → write `review_response_<PR#>.md` → independent review of the plan → implement and verify → **publish** (push, reply on every thread, update the PR) → report.

Use the grilling session to settle judgment calls. In execute mode, ask for approval of the reviewed change plan before implementation and approval of the verified revision and exact payload before publication.

## Conventions

Facts are your legwork. Whatever the PR, the code, the ticket, or a command can answer gets looked up. Where a missing input has a safe default, take it and say so in the session's opening status instead of asking.

**Main loop and subagents.** The main loop owns everything that talks to the user or writes shared state: the grilling, the plan file, the final call on each review finding, commits, and the publish step. `general-purpose` subagents take bulky, self-contained work and return text. A subagent costs more than the context it saves when the work is small, so on a small PR (a handful of items in a few files, a gate that runs in seconds, a short findings list) do that work in the main loop. When you do delegate, launch independent subagents in one message so they run concurrently, and give each a self-contained prompt: absolute paths, the item bodies it needs, how to read the PR head, and the result shape to return.

**Helper script.** `python3 "<skill-dir>/scripts/pr.py"` does the GitHub plumbing (`fetch`, `reply`, `body`) and is written as `pr.py` below.

**Placeholders.** Create one scratch directory with `mktemp -d` and record its path as `<tmp>`. `<pr>` is the PR link, `<n>` its number, and `pr.url`, `head_oid`, and the like are fields of the Step 0 snapshot. Substitute the values yourself: shell variables do not survive between Bash calls.

**Voice.** Replies are posted under the user's GitHub login, so write them as the user: first person, direct, technical, respectful. Acknowledge what is right in a comment before disagreeing, and commit to specifics ("extracted this into `X` and added a test for `Y`") over "good point, fixed". Cite code by symbol or test name: the fix moves line numbers before the reply is read. Leave out emojis, signature lines, and any note on how the reply was produced.

## Step 0 - Snapshot the PR and pick the mode

```bash
python3 "<skill-dir>/scripts/pr.py" fetch [<PR-URL | PR-number>] --out "<tmp>/pr.json"
```

With no argument it uses the current branch's PR. It prints the counts and writes one JSON snapshot: `pr` (`url`, `title`, `body`, `author`, `state`, `head_ref`, `head_oid`, `head_repo`, `base_ref`), `viewer` (the login replies post as), `threads` (each with `root_comment_id`, `path`, `line`, `is_resolved`, `is_outdated`, `comment_count`, `thread_version`, `diff_hunk`, `comments`), `reviews` (summary bodies and their `state`), `conversation` (top-level comments), and `ticket_candidates`. Exit 2 means no PR resolved: ask for the link. For authentication errors, ask the user to run `gh auth login` or provide approved repository access.

Then settle three things:

- **Something to answer.** The items are every unresolved thread, plus each review summary or conversation comment that asks for something (bot and CI noise, acknowledgements, and the author's own comments ask for nothing). With no items, say so and stop.
- **Mode.** *Execute* needs the PR head checked out here: `gh pr view --json number` on the current branch resolves to this PR, `head_oid` is `HEAD` or an ancestor of it (`git merge-base --is-ancestor`), tracked files are clean (`git status --porcelain --untracked-files=no`), and the PR is `OPEN`. Local commits ahead of `head_oid` are fine: the publish round lists them. A miss becomes the first question of the Step 3 session. Its recommended answer is the remedy (`gh pr checkout <pr.url>` on a clean tree, `git pull --ff-only` when behind, commit or stash for local changes) and it names *plan-only* as the alternative. Plan-only writes the local plan and uses read-only Git and GitHub operations; it is the only mode when this directory is not a clone of `head_repo` or the PR is closed.
- **Plan file.** The plan is `review_response_<n>.md` in the current directory. Keep it out of commits. Reuse an existing entry and its decisions only when the recorded PR head and thread version both match the new snapshot. If the head moves, recheck all evidence and refresh affected decisions. Preserve posted reply URLs as history. Redo changed threads, add new ones, and mark resolved threads.

## Step 1 - Gather evidence

Read the repository guidance first. Cite it when a reviewer's request conflicts with it.

Read the flagged code, tests, and branch specs with `git show <head_oid>:<path>` so local edits cannot change the evidence. If `git cat-file -e <head_oid>^{commit}` fails, fetch the PR ref in execute mode. In plan-only mode or outside a clone, use the GitHub contents API with `ref=<head_oid>`. Report unavailable evidence if it cannot be read at that revision.

Two kinds of evidence, gathered together:

- **The ticket**, when the PR links one or `ticket_candidates` suggests a Jira key. Use the repository's configured GitHub or Jira tools. If the context is unavailable, ask for the relevant acceptance criteria or record the gap.
- **One evidence row per item**, clustering related items (same file or subsystem, a shared root cause, explicit cross-references) so each cluster is read once. Check three sources: the **code** at the flagged site (the whole hunk the comment sits on, since a vague comment often points at a defect a line or two away), the **tests** that cover it (does a test already settle the reviewer's concern, contradict it, or is it untested), and the **specs** (`specs/<name>/` requirements, plan, and validation docs for this branch, plus any design doc the PR cites). The row: `item id - what the code does there, with file:line - what the tests cover or miss - what the spec says, or "no spec coverage" - the reviewer's claim holds: yes / partially / no, with a one-line reason`.

**Done when** every item has an evidence row.

## Step 2 - Classify and draft

Decide each item on its evidence, weighing the ticket's acceptance criteria as the statement of intended behavior:

- **Classification**
  - `Agree` - the reviewer is right; plan the fix.
  - `Agree with modification` - the concern is valid, a different remedy is better; plan that one and say why. Before asking the user to prefer your remedy over the reviewer's, confirm it works against the head code (trace it, or prototype it in `<tmp>`) and name what it changes for existing callers.
  - `Push back` - the code is right as written. The case rests on code behavior, a test, a spec section, or a ticket criterion, never on preference or seniority.
  - `Needs clarification` - the comment is ambiguous or rests on an unstated assumption; draft the specific question that would settle it.
- **Evidence** - the file:line, test, spec, and ticket citations behind the classification.
- **Action** - for the two `Agree` classes: the files, the approach, the tests to add or change, any spec update when behavior changes, and a size (S / M / L). Otherwise "no code change".
- **Reply** - the text to post, in the *Voice* above, written as it will read once the work has landed: past tense, with a named placeholder such as `<sha:boundary-fix>` for each commit it cites, one name per planned commit.

Then look across the items: name each **cross-cutting theme** (three comments pointing at one missing abstraction get one action, not three), order the actions so a fix that settles several comments is done once, and flag any item whose fix changes the PR's scope enough to belong in a follow-up ticket. Resolved and outdated threads are listed for completeness and get no action unless their concern is still live in the head code. A defect the evidence turned up that no reviewer raised joins an action only when it shares that action's root cause; otherwise it goes to the plan's Open questions. No reply may lean on something the evidence showed to be false.

**Done when** every item has exactly one classification, its evidence, an action, and a reply.

## Step 3 - Grill the user on the contested calls

Load Matt Pocock’s installed `grilling` skill before the interview. On Codex use the skill registry entry `mattpocock-skills:grilling` and read its registered instructions. On Gemini CLI activate `grilling` through the skill tool. Run the interview as instructed there. If it is missing or disabled, pause the interview and name the missing skill. On Codex, run `codex plugin marketplace add mattpocock/skills` and `codex plugin add mattpocock-skills@mattpocock`. On Gemini CLI, run `gemini skills install https://github.com/mattpocock/skills.git --path skills/productivity`. Reopen the session and confirm discovery before continuing.

Seed the design tree with what is the user's to decide, each question carrying the evidence behind its recommended answer:

- **Execution blockers** from Step 0, in the first round.
- **Push backs** - each one. The user owns the relationship with the reviewer, so they see the reviewer's point, the evidence, and the stance before it is taken in their name.
- **Agree with modification** - the reviewer's remedy against the one planned.
- **Clarifications** - each one: the user may know what the reviewer meant, and the question goes to the reviewer only if they do not.
- **Scope** - an L-sized fix, or one that changes what the PR delivers: in this PR, or a follow-up ticket.
- **Intent gaps** - a classification that turns on product intent neither the spec nor the ticket settles.
- **Ambiguous ticket** - only when Step 1 kept more than one.

With nothing contested, the session is one confirmation round.

**Done when** the frontier is empty and the user has confirmed shared understanding. List the **settled decisions** (`D1`, `D2`, ...) in the conversation: Step 4 records them, Step 5 checks findings against them.

## Step 4 - Write the plan

Write `review_response_<n>.md` in this order:

1. **Header** - PR link, title, author, branches, snapshot `head_oid`, ticket context and status or the source gap, date, mode, and item counts (total / unresolved / resolved or outdated). In plan-only mode, identify every proposed reply as a draft.
2. **Summary table** - one row per item: anchor (`path:line`, reviewer, first-line excerpt), classification, size.
3. **Settled decisions** - `D1...Dn` from Step 3.
4. **Cross-cutting themes** - each shared root cause and the one action that addresses it.
5. **Per-item detail** - the comment (quoted), classification, evidence, action, reply, dependencies on other items, and a `Posted:` line. A thread records its `root_comment_id` and `thread_version` from the snapshot, which Step 7 posts with; review summaries and conversation comments record their `id` and are answered together in the one conversation comment.
6. **Execution order** - a numbered checklist of the code, test, and spec changes in the order to make them, grouped into the planned commits.
7. **Open questions** - anything the user deferred, clarifications awaiting a reviewer, and defects no reviewer raised.
8. **Plan review** - the Step 5 disposition table.

The plan states only what has happened: commit placeholders stay placeholders until Step 6 creates the commits, checklist boxes stay unticked until the work is done, and `Posted:` stays empty until Step 7 returns a URL.

## Step 5 - Independent review of the plan

Use [the review instructions](review.md) with the plan path, pinned Git revision, source evidence, and settled decisions. Verify each finding and record its disposition in the plan. Reopen material decisions with the user and recheck any revised plan. If review is pending, deliver the plan and handoff before executing it.

In plan-only mode, go directly to Step 8 and report the local plan. In execute mode, obtain approval of the reviewed change plan before proceeding to Step 6.

## Step 6 - Implement and verify

Work through the plan's Execution order on the checked-out PR branch, one planned commit at a time:

- **Test first** wherever an action changes behavior: write the test that fails on the reviewer's scenario, then the fix. Follow the repo's own conventions, layering, and test idioms.
- **Stay inside the plan.** Make the smallest change that satisfies the item. When an action proves wrong or wider than planned, update its entry in the plan; if that touches a settled decision, reopen that branch with the user before continuing.
- **Commit each action or theme when its tests pass**, before starting the next edit to a file it shares with a later commit, so every commit stages whole files. These are new commits on top of the branch: reviewers follow "changes since my last review", which amended or rebased history erases, and a fast-forward push never needs force. Match the repo's commit convention from `git log`, stage explicit paths (`git add -- <path>...`), and include the trailers the environment requires. Independent M or L actions in separate files may go to subagents launched together; the main loop commits their work.
- **Gates.** With the commits in, run the project's format, lint, build, and full test gates over `HEAD`, using the commands the repo defines in `specs/tech-stack.md`, repository guidance, CI, or the task file, each bounded by a timeout. Fix a failure this work caused in a further commit and run all of them again; the same applies when a commit hook rewrites files. A failure that also reproduces at `head_oid` (check in a throwaway `git worktree`) predates this work: put it to the user (fix it, stop, or publish with the waiver named in the PR). A gate the repo does not define is reported as not configured, never as green.

Then fill each commit placeholder in the plan's replies with its short SHA, and re-read every reply against `HEAD`: each one must describe what the code now does.

If a required check is unavailable, report the cause and keep publication pending unless the user explicitly waives it.

**Done when** every planned action is committed, the gates are green on `HEAD`, the tree is clean apart from the plan file, and no reply holds a placeholder.

## Step 7 - Publish

Nothing has left the machine yet, and prepare the ready-to-send payload and present it for explicit approval of the verified revision.

**Prepare** in `<tmp>`:

- `replies.json` - one `{"reply_to": <root_comment_id>, "seen_thread_version": "<thread_version>", "body": "..."}` per thread, and at most one `{"conversation": true, "body": "..."}` that answers the review summaries and top-level comments together, quoting each point it answers.
- `pr-section.md` - what changed in response to review, by theme with commit SHAs, and what was deferred (with its ticket, or "no ticket yet"). Where a change makes a statement in the existing description false, say so here; the rest of the description stays as its author wrote it.
- The outgoing commits (`git log --oneline <head_oid>..HEAD`) and the push destination: `head_ref` on the remote the current branch pushes to (`branch.<current>.pushRemote`, else `branch.<current>.remote`).
- The reviewers to re-request: those who requested changes and whose threads all receive a reply.

Run `pr.py reply <pr> "<tmp>/replies.json" --dry-run` to learn which threads would be held.

**Publish round** (one question, grilling format). Show the destination and the outgoing commits; each reply as one line (`path:line - reviewer - classification - what the reply says, in a few words`), with the plan path for the full text; the PR section; the reviewers to re-request; anything the dry run would hold. "Yes" publishes all of it, and the user may strike any part.

Confirm the approval still covers the verified revision and the exact payload. Send only approved actions in this order. Proceed after each required predecessor succeeds.

1. **Push** with `git push <remote> HEAD:refs/heads/<head_ref>`; with no outgoing commits, still verify the PR head before replying. A rejected push means the branch moved: stop and put it to the user; force is theirs alone to choose. Verify with `pr.py fetch <pr> --out "<tmp>/pr-after.json"`: `pr.head_oid` must equal `git rev-parse HEAD`. GitHub can lag by some seconds, so try up to three times. Replies citing commits the reviewers cannot see would mislead, so an unverified push ends the step here.
2. **Reply** with `pr.py reply <pr> "<tmp>/replies.json" --expect-head <verified-head>`. Write each `posted` URL into its item's `Posted:` line. A `held` thread disappeared, was resolved, or changed after the snapshot, so its reply may no longer fit: leave it unanswered and report it with the latest comment. Report a `failed` reply with its exact error; one attempt each.
3. **Update the description** with `pr.py body <pr> "<tmp>/pr-section.md" --expect-head <verified-head>`. It replaces only this skill's marked block, so a later round updates the block instead of stacking another.
4. **Re-request review** with `gh pr edit <pr.url> --add-reviewer <logins>` after confirming the remote head is still the approved revision. Leave out any reviewer with a held or failed thread.

Threads stay unresolved: resolving one is the reviewer's acknowledgement to give.

**Done when** each part the user approved is sent and verified, or reported with the reason it was not.

## Step 8 - Report

Remove `<tmp>`, then report. Keep it short, and point at the plan file for the detail:

- **Plan** - the path; item counts per classification; the ticket used, or that it was unavailable.
- **Review** - reviewer and revision, or the pending handoff; findings accepted / rejected / deferred, with one line per rejection.
- **Changes** - the commits, and each gate as pass / fail / not configured, naming any waiver.
- **Published** - the push and its verified head; replies posted, held, and failed, each held or failed one with its reason; the PR description update; the reviewers re-requested. In plan-only mode: that nothing was changed or posted, and what has to be true to execute.
- **Open** - clarifications awaiting reviewers, deferred items and their follow-up tickets, and any remaining risk.
