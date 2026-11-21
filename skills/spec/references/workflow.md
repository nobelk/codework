Paths written as `<skill-dir>` resolve from the folder containing the activated SKILL.md.

# Spec

Write `specs/<name>/requirements.md`, `plan.md`, and `validation.md` for one phase or task. Work from the repository root and read its guidance.

## Step 1 - Select the scope

Use the explicitly requested phase, local brief, or configured tracker item. With no input select the next unstarted phase whose dependencies are satisfied in `specs/roadmap.md`. Ask for the intended scope if there are several candidates, a named input is inaccessible, or the roadmap is missing and no task was supplied. If `constitution` can supply missing project standards, name the missing documents. For an in-progress phase, locate and read its existing spec before revising it.

## Step 2 - Select the checkout

Follow the repository’s branch convention and preserve any unrelated changes. If the project uses phase worktrees, reuse the matching worktree or create a new one from the pinned base with `git worktree add`. Otherwise work in the selected checkout. Pass its absolute path as the working directory for every command and reviewer. If the user requests rebasing an existing phase branch, use Codework’s `rebase` workflow and resume after it restores local work. Confirm worktree and branch identity before editing.

## Step 3 - Read the constitution and the code

In one message, in the worktree:

- Read the phase's roadmap entry and `specs/mission.md`, which bound the scope.
- Read `specs/tech-stack.md`. Its *Architecture and conventions* and *Testing and quality gates* sections are the engineering standards the plan has to follow.
- Read `AGENTS.md`, `GEMINI.md`, and repository guidance and the architecture or convention docs they cite. Their rules bind the plan too, and win where they are more specific.
- Survey the code directly or use a read-only exploration subagent: the packages involved, their public interfaces, and how the existing tests reach them. The seams and task groups below are only as good as this picture.

Read the PRD, design, and linked ADRs where available. For a standalone task without a constitution, record the available sources and any missing standards before settling the plan.

## Step 4 - Grill the user (`grilling` skill)

Load Matt Pocock’s installed `grilling` skill before the interview. On Codex use the skill registry entry `mattpocock-skills:grilling` and read its registered instructions. On Gemini CLI activate `grilling` through the skill tool. Run the interview as instructed there. If it is missing or disabled, pause the interview and name the missing skill. On Codex, run `codex plugin marketplace add mattpocock/skills` and `codex plugin add mattpocock-skills@mattpocock`. On Gemini CLI, clone upstream with `git clone https://github.com/mattpocock/skills.git mattpocock-skills` and run `gemini skills install ./mattpocock-skills/skills/productivity`. Use an existing upstream checkout if available. Reopen the session and confirm discovery before continuing.

Seed the design tree from the roadmap entry and the Step 3 reads, so every question and recommended answer is specific to this phase. Cover at least:

- **Scope:** what is in and out for this phase. The roadmap entry is the starting point, not the final word.
- **Key decisions:** every consequential open choice (library, data model, sync vs. async, auth, ...), each with its trade-off. A choice the spec makes without the user gets frozen silently.
- **Test seams:** the public interfaces this phase's tests will exercise, each with a one-line note on what it catches and what it misses. The `tdd` skill that `code` follows allows no test at an unconfirmed seam, so confirming them here is what lets `code` build without stopping to ask.
- **Validation:** how we will know the phase is done (tests, manual QA, metrics, ...).
- **Repo-mandated content:** anything `AGENTS.md`, `GEMINI.md`, and repository guidance requires a spec to state. Each one is a decision for the user, even when the answer looks obvious.

Ask only questions whose answer changes the spec.

**Done when** the frontier is empty and the user confirms you share an understanding. List the settled decisions as `D1`, `D2`, ... in the conversation; Step 5 writes from them and Step 7 checks findings against them. Write nothing under `specs/<name>/` until then.

## Step 5 - Write the spec files and mark the phase

In revise mode, keep existing decisions, ordering, and evidence where still valid. Confirm the new scope before changing them.

Write for an implementer who reads these files cold and can't ask what you meant.

### `requirements.md`

- **Context:** the selected phase number and name or task, linked to the relevant roadmap, mission, tech stack, PRD requirement IDs, design sections, and ADRs.
- **Scope:** `In:` / `Out:` lists, from the settled scope decisions.
- **Decisions:** every other settled decision, numbered `D1`, `D2`, ... as in the session, plus the constraints inherited from the mission and tech stack.

### `plan.md`

Open with a short **Standards** section. Name the documents that govern this plan (the two `tech-stack.md` sections, `AGENTS.md`, `GEMINI.md`, and repository guidance, any doc they cite) rather than restating them, and add only what is specific to this phase: for example a design pattern a task group needs, named by its well-known name with the reason plain code isn't enough. Where the repo documents no standards at all, state the defaults here instead: dependencies point inward, behavior changes are test-first through public interfaces, plain code before patterns, and style follows the surrounding code.

Then write the **task groups**, numbered, in this shape:

```markdown
## 2. <Task group name>
- **Depends on:** 1
- **Requirements:** <requirement IDs addressed by this group>
- **Seam:** <the agreed public interface its tests exercise>
- **Tests first:** <the behaviors to pin, each as a failing test written before its code>
- **Then:** <the code, migrations, or config that make them pass, and the package or layer they land in>
```

`code` runs the groups as a task graph: a group starts once the groups it depends on are merged, and independent groups may run in isolated worktrees when the host permits concurrent delegation. That shapes how to cut them:

- **Each group is a vertical slice** that leaves the branch building and its tests green, and is small enough for one implementer. Group 1 is the smallest slice that works on its own.
- **`Depends on` lists only real blockers** (`-` for none). Every needless edge forces work into sequence.
- **Groups that can run side by side edit different files.** If two groups need the same file, make one depend on the other.
- **Every group names a seam from the settled list.** A group that needs a seam nobody agreed to means Step 4 isn't finished.

### `validation.md`

- **Success criteria:** from the settled validation decisions.
- **Checklist:** concrete checkboxes for the tests to add, the repo's quality gates (format, lint, build, the full test suite, any architecture or static-analysis checks), manual checks, and metrics to confirm. `code` ticks the boxes it verifies and leaves the manual ones for the PR's reviewer.
- **Done when:** one line naming the binary signal, consistent with the roadmap entry's own `Done when`.

### Roadmap status

If the phase has a `Status:` line in `specs/roadmap.md`, set it to `in progress`. That is the only change to `roadmap.md`. If the roadmap has no status fields, or already had uncommitted changes you didn't make, leave it alone and say so in the report.

## Step 6 - Independent review

Use [the review instructions](review.md). Include the trace from requirements and design to task groups and acceptance checks.

## Step 7 - Adjudicate the findings and update the spec

Verify findings against the sources before acting on them. With more than about 5, split them into batches of 3-5 (contradictory findings share a batch) and launch one subagent per batch in a single message, each with the settled decisions and the constitution's constraints; the final call on each finding stays here. For each finding:

1. Re-read the cited passage and confirm the issue is real.
2. Check it against the settled decisions, the mission, and the tech stack.
3. Give it a disposition:
   - **accept** - a real gap or contradiction. Edit the file(s), keeping each edit traceable to its finding number.
   - **reject** - wrong, a deliberate scope cut, or only preferring a different choice than one the user made. Say why.
   - **defer** - valid but it belongs to a later phase, or needs a user decision that can wait. Say where it goes.

A finding you would otherwise accept that changes a settled decision (wider scope, a different key choice, a new seam), or one showing that a decision rests on a wrong fact or is unsafe, is the user's call. Reopen that branch with the grilling skill, update the decision list, and then edit. Show the user the full disposition table.

## Step 8 - Validate and hand off

Check that every in-scope requirement has an acceptance check and each task has an agreed seam, dependencies, and expected test evidence. Record commands for applicable unit, functional, fuzz, mutation, and chaos tests, plus mandatory format, lint, type/build, and full test gates. Explain why any test category is inapplicable.

Present the three paths, phase or task, dependency order, revision under review, checks, and any review handoff. Leave the artifacts local for the user to approve. Commit or publish only with the user’s authorization. Pass the selected spec path to `code`.
