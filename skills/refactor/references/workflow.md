Paths written as `<skill-dir>` resolve from the folder containing the activated SKILL.md.

# Refactor skill

Act as a principal engineer refactoring a branch before it merges. The flow:

resolve the branch and its PR → baseline the gates → review the branch's changes for architecture drift and clean-code violations → triage findings into plan items → **grill** the user on the judgment calls → write `refactor-<PR#>.md` → independent review of the plan → apply it, one behavior-preserving commit per item → **publish** (push, update the PR) → report.

The standard: code is clean if it can be understood easily, by everyone on the team, and changed by someone other than its author. Every plan item has to move the code toward that. Two consequences shape the whole run:

- **A refactor preserves behavior.** The tests that pass before must pass after, and code no test pins gets a test before it is touched. A change in what a caller observes is a *correctness item*: the user's call, never slipped into a cleanup.
- **"No refactor warranted" is a legitimate result.** A plan that invents work to look thorough costs the reviewer as much as one that misses a violation. When the evidence supports it, say so and stop.

## Files in this skill

- `<skill-dir>/CLEAN_CODE.md` - the principles, with the rule ids findings cite and how to apply them. Read it before Step 1; pass its absolute path to every reviewing subagent.
- `<skill-dir>/ARCHITECTURE.md` - the architecture-conformance procedure and its result shape (Step 1).
- `python3 "<skill-dir>/scripts/pr.py"` - finds, opens, and updates the branch's PR; written as `pr.py` below.

## Conventions

Before asking the first decision, load Matt Pocock’s installed `grilling` skill. On Codex use the skill registry entry `mattpocock-skills:grilling` and read its registered instructions. On Gemini CLI activate `grilling` through the skill tool. Run the interview as instructed there. If it is missing or disabled, pause the interview and name the missing skill. On Codex, run `codex plugin marketplace add mattpocock/skills` and `codex plugin add mattpocock-skills@mattpocock`. On Gemini CLI, clone upstream with `git clone https://github.com/mattpocock/skills.git mattpocock-skills` and run `gemini skills install ./mattpocock-skills/skills/productivity`. Use an existing upstream checkout if available. Reopen the session and confirm discovery before continuing.

Facts are your legwork. Whatever the code, the docs, or a command can answer gets looked up. Where a missing input has a safe default, take it and say so in the session's opening status instead of asking.

**The repo's rules outrank this skill.** Read `AGENTS.md`, `GEMINI.md`, and repository guidance first when they exist: conventions, layering, test expectations, commit style, and gates come from there, and from the surrounding code, before they come from `CLEAN_CODE.md`.

**Main loop and subagents.** The main loop owns everything that talks to the user or writes shared state: the grilling, the plan file, the final call on each finding, every code change and commit, and the publish step. `general-purpose` subagents take bulky read-only work and return text. A subagent costs more than the context it saves when the work is small, so on a small branch (a few hundred changed lines, gates that run in seconds, a short findings list) do that work in the main loop. When you do delegate, launch independent subagents in one message, and give each a self-contained prompt: absolute paths, the files it owns, and the result shape to return.

**Ids.** `CLEAN_CODE.md` owns the short rule ids (`D5`, `F6`, `SM2`), and specs often number requirements `R1...`. So this run's own ids are spelled out: findings `FND-1`, refactor items `RF-1`, correctness items `COR-1`, settled decisions `DEC-1`. An id never changes once it has been shown to the user or a reviewer; new entries take the next free number.

**Placeholders.** Create one scratch directory with `mktemp -d` and record its path as `<tmp>`. `<branch>`, `<slug>` (the branch name with `/` replaced by `-`), `<base>`, `<merge-base>`, `<start>` (the branch tip when the run began), and `<id>` are values you resolve in Step 0 and substitute yourself: shell variables do not survive between Bash calls.

## Step 0 - Resolve the branch, the workspace, and the PR

- **Branch.** The argument, or the current branch. A detached `HEAD` with no argument has nothing to push to: ask which branch.
- **Workspace.** Work where the branch is checked out, and leave every other checkout alone. If it is the current branch, that is here. If another worktree has it (`git worktree list --porcelain`), work there. Otherwise add one beside the repo, never inside it: `git worktree add <repo-parent>/<repo-dirname>-worktrees/<slug> <branch>` (for a branch that exists only on the remote: `-b <branch> origin/<branch>`). Use that absolute path as the working directory for all commands, checks, and reviewers.
- **PR and base.** Use the requested comparison base when supplied. If GitHub access is available, `pr.py find <branch>` can supply the PR number, head, and base branch. Otherwise use the repository's local default branch or ask for a base. Refresh a remote-tracking base by explicit refspec when needed. Pin its SHA and record the merge base with HEAD. Use the PR number or branch slug for the plan name.
- **Ready to work.** Tracked files are clean (`git status --porcelain --untracked-files=no`), and the branch is not behind its remote. A miss is the first question of the Step 3 session, with the remedy as its recommended answer (commit or stash; `git pull --ff-only`).
- **Scope.** The source and test files the branch changed: `git diff --name-status <merge-base>...HEAD`, less generated code, vendored code, and lockfiles. This is what the review judges. A plan item may edit a file outside the scope when the change requires it (the callers of a renamed function, the home of a new port), but the review does not go looking for trouble there. With no delta (the branch is the default branch), ask which paths to review; a whole repository is never the assumed scope.
- **Plan file.** `refactor-<id>.md` in the workspace root (for PR 123: `refactor-123.md`): a working document that is never staged or committed. When it, or `refactor-<slug>.md` from a run before the PR existed, is already there, update it in place under the current name: items marked done keep their commit and are not replanned.
- **Baseline.** Record `<start>` = `git rev-parse HEAD`, then run the repo's gates as the repo defines them (`specs/tech-stack.md`, repository guidance, the CI config, the task file): format check, lint, the architecture gate, build, and the full test suite, each bounded by a timeout. Record each as pass / fail / not configured, and keep the outputs in `<tmp>`. This is the reference "behavior preserved" is measured against. A failing lint or architecture gate is evidence for Step 1. A failing **test** means nothing can prove a refactor safe: it is a first-round question (fix it first in its own commit, keep the failing area out of scope, or stop).

## Step 1 - Review the branch

Read `CLEAN_CODE.md`, then review the scope along two axes. On a larger branch, fan out in one message: one subagent on architecture, and one per cluster of related files on clean code, production and test code alike.

- **Architecture drift**, following `ARCHITECTURE.md`: build the model of what the repo declares, then check what the branch added against it. It returns the style and where it is declared, the gate result, the new dependency edges, and the conformance rows.
- **Clean code**, against `CLEAN_CODE.md`: read each file in full, with its neighbours and its tests, and judge it rule by rule. Check how far a change would reach before proposing it (the language server's find-references where there is one; a search otherwise). Also read the branch's spec (`specs/<name>/`) when there is one, to tell intended behavior from accident.

Each finding, from either axis, carries the same fields (a table reads best):

- **site** - `file:symbol`
- **rule** - a `CLEAN_CODE.md` id, or an architecture rule as `doc:line`
- **problem** - what is wrong, with `file:line` evidence, and what it costs a reader or the next change
- **remedy** - as a named refactoring
- **behavior-preserving** - yes or no, and why
- **pinned by** - the tests that would fail if the remedy went wrong, or `unpinned`
- **payoff and cost** - H / M / L against S / M / L

**Done when** every in-scope file has been read in full and either has findings or is recorded as clean.

## Step 2 - Triage findings into plan items

Findings are raw material; the plan is made of items. In the main loop:

1. **Group by root cause** (G4). Five findings that all follow from one missing value object are one item, fixed at the root. A smell (SM1-SM6) is never an item by itself: trace it to the design, object, or function rule behind it.
2. **Give every finding one verdict.**
   - `plan` - the payoff justifies the cost and the remedy preserves behavior.
   - `skip` - real, but the remedy costs more than it returns, or would make the code more complex than it is (G2). Recorded under Non-goals with the reason.
   - `correctness` - the finding is a bug, or its remedy would change what a caller observes, even only for malformed input. Never planned as a refactor; put to the user in Step 3.
   - `observation` - pre-existing and outside the scope. Recorded, not planned.
3. **Pin before touching.** Where planned code is `unpinned`, the plan opens with a safety-net item: characterization tests of what that code does today, at the boundary callers rely on, committed before any refactor so that a behavior change turns them red. Pin what the items will touch and stop there. A test that pins an accident (a bug, a quirk on malformed input) says so in its name or a comment: kept, not endorsed.
4. **Order the items** so each one's prerequisites come first and no two fight over the same lines: the safety net, then architecture moves (a concern to its right home, a port at its consumer), then design (value objects, polymorphism, injection), then functions and names, then comments and layout, since everything above rewrites them. The order is between items: one that rewrites a unit wholesale carries that unit's naming and comment findings with it. Each item is one commit. Correctness items the user approves come last, each in its own commit with its regression test, so the refactor can be read and verified without them.

When every finding is `skip` or `observation` and the architecture verdict is `conforms`, there is nothing to refactor: write the plan with its verdicts and evidence, report, and stop.

**Done when** every finding has a verdict and every `plan` finding belongs to exactly one item.

## Step 3 - Grill the user


A rule the repo documents is a fact, not a question. Seed the design tree with the decisions this branch actually raises, each carrying the evidence behind its recommended answer:

- **Blockers** from Step 0, in the first round.
- **Depth** - surgical (names, comments, dead code, local extraction), moderate (plus deduplication, value objects, split functions), or structural (plus moving code between components and adding ports). Recommend from the findings, and name in the same question each move across components that the recommended depth includes; a move the user might reasonably defer gets its own question, with the cost of deferring stated.
- **Public surface** - a rename or signature change that callers outside this repository would see.
- **Correctness items** - each bug or behavior change found: fix it now in its own commit with a regression test, or defer it. Where a planned refactor cannot avoid changing an edge-case behavior, the choice is to accept the change, named in that item's commit and in the PR, or to drop the item.
- **Convention conflicts** - where a principle and the repo's established idiom disagree and neither the repo nor `CLEAN_CODE.md`'s precedence settles which wins.
- **Test restructuring** - how far to take T1 where the tests bundle many assertions.

**Done when** the frontier is empty and the user has confirmed shared understanding. List the **settled decisions** (`DEC-1`, `DEC-2`, ...) in the conversation: Step 4 records them, Step 5 checks findings against them.

## Step 4 - Write the plan

Write `refactor-<id>.md` in this order:

1. **Header** - branch, PR link or "no PR", base and `<merge-base>`, `<start>`, the scope (file count and changed lines), the baseline gate results, the date.
2. **Settled decisions** - `DEC-1...DEC-n`.
3. **Architecture** - the style and where it is declared (or "inferred", with the evidence), the gate result, the conformance table, and the verdict.
4. **Findings** - the Step 1 table, each `FND-n` with its Step 2 verdict.
5. **Items** - in execution order, each `RF-n` with: a title; the findings it resolves; the files and symbols it touches, in scope and outside it; the refactoring steps; why it preserves behavior; the tests that pin it; the commit subject, in the repo's convention; and a `Status:` line (`planned`) with an empty `Commit:`.
6. **Correctness items** - each `COR-n`, with the user's decision; the approved ones carry the same fields as an item.
7. **Non-goals** - the skipped findings with their reasons, and the observations outside the scope.
8. **Plan review** - the Step 5 disposition table.

The plan states only what has happened: `Status:` stays `planned` and `Commit:` stays empty until Step 6 does the work.

## Step 5 - Independent review of the plan

Use [the review instructions](review.md) with the plan path, pinned Git revision, source evidence, and settled decisions. Verify each finding and record its disposition in the plan. Reopen material decisions with the user and recheck any revised plan. If review is pending, deliver the plan and handoff. Obtain approval of the reviewed plan before executing it.

## Step 6 - Apply the plan

Work through the items in order, one commit each:

- **Take small steps.** Apply the named refactoring a step at a time and run the tests that pin it after each step. A red test means the step changed behavior: undo it and take a smaller one. In a refactor commit, edit a test only where it was coupled to the structure being changed (it imported a moved symbol, or called a function that was split), never to accept a different result. A correctness commit is the exception: it updates the test that pinned the old behavior, and adds the regression test.
- **Stay inside the item.** Something new noticed on the way is a note for the plan, not an extra edit: a new item at the next free id, a Non-goal, or, when it touches a settled decision or is a correctness item, a reopened question.
- **Commit the item** when its tests pass: the subject the plan named, in the repo's convention from `git log`; explicit paths (`git add -- <path>...`); the trailers the environment requires. New commits on top of the branch, never amended or rebased, so a reviewer can read the refactor item by item. Set the item's `Status:` to `done` and fill its `Commit:`.

With every item in, verify against the baseline:

1. **Gates and tests.** Run all the gates and the full suite again. Every test that passed at `<start>` still passes, or is accounted for by name (renamed, split, moved); every gate that passed still passes; a gate that failed because of a planned finding now passes.
2. **Outputs, where they can be compared.** Passing tests prove only what the tests assert. When the code has a boundary whose output depends only on its input (a CLI, a pure function, a serializer), run it at `<start>` (a throwaway `git worktree add --detach <tmp>/start <start>`, removed afterwards with `git worktree remove --force`) and at `HEAD` over a generated spread of inputs, edge cases included. The only differences allowed are the ones an approved correctness item explains.
3. **A second look.** Read the whole change once (`git diff <start>..HEAD`) against `CLEAN_CODE.md`: a refactor that introduces a new finding has not left the code cleaner (G3).

Anything these turn up is fixed in a further commit, recorded as a new item, and the checks run again.

**Done when** every item is `done` with its commit, the three checks hold, and the tree is clean apart from the plan file.

## Step 7 - Optional approved publication

If requested as a local cleanup, proceed to the report. For publication, prepare `<tmp>/pr-section.md`: the architecture verdict before and after; the items applied, each with its commit and the rules it addressed; every behavior change, called out as such with a before-and-after example; what was deferred or skipped and why; the gates, before and after. Where the refactor makes a statement in the existing description false, say so in the section.

**Publish round** (one question, grilling format). Show the push destination (`<branch>` on the remote it pushes to), the outgoing commits (`git log --oneline origin/<branch>..HEAD`), and the PR section. With no open PR, the question also proposes opening one against `<base>`, with its title and a short summary of what the branch delivers (from its commits and spec). "Yes" publishes all of it, and the user may strike any part.

**Send**, each step only after the one before it succeeded:

1. **Push** with `git push <remote> HEAD:refs/heads/<branch>`. A rejected push means the branch moved: stop and put it to the user; force is theirs alone to choose.
2. **Verify** that `git ls-remote <remote> refs/heads/<branch>` shows `git rev-parse HEAD`.
3. **Update the PR** with `pr.py body <pr-url> "<tmp>/pr-section.md"`, which replaces only this skill's marked block, so a later run updates it instead of stacking another. With no PR and the user's yes, open one with `pr.py create <branch> <base> "<title>" "<tmp>/pr-summary.md" "<tmp>/pr-section.md"`: the summary becomes the description and the section goes beneath it in the marked block. Then rename the plan file to `refactor-<number>.md`, the name a later run looks for.

**Done when** each part the user approved is sent and verified, or reported with the reason it was not.

## Step 8 - Report

Remove `<tmp>`, then report. Keep it short, and point at the plan file for the detail:

- **Plan** - the path; the architecture verdict before and after; items applied, skipped, and deferred.
- **Review** - reviewer and revision, or the pending handoff; findings accepted / rejected / deferred, with one line per rejection.
- **Changes** - the commits; each gate before and after as pass / fail / not configured; the test count before and after; every behavior change, with its commit.
- **Published** - the push and its verified head; the PR updated or opened, with its URL; or what was not sent and why.
- **Open** - correctness items deferred, observations outside the scope, and any remaining risk. When the run used a worktree, its path and that it stays until the PR merges.
