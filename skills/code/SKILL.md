---
name: code
description: Implement a selected Codework spec or ticket with test-driven changes, repository quality gates, independent review, and approval of the current revision.
license: Apache-2.0
---

# Code

## 1. Pin the scope and checkout

Accept a spec path, phase name, or `specs/<name>` branch with `requirements.md`, `plan.md`, and `validation.md`. With no argument, use the phase named by the current `specs/<name>` branch when it contains the spec. For a ticket, read the [tracker handoff](references/trackers.md). If there is no usable input, ask for the selected phase, spec, or ticket before editing. Record the base revision, working directory, and starting branch. Use the existing phase worktree when available and preserve unrelated index and working tree changes.

Read the spec, its linked PRD, design and ADRs, the mission and roadmap, and the **Architecture and conventions** and **Testing and quality gates** in `specs/tech-stack.md`. Read repository guidance and CI for more specific rules. Map task IDs to requirements, acceptance criteria, and the commands that verify them. Identify blockers and file ownership before scheduling. Treat a legacy plan without any `Depends on` lines as sequential. Ask the user to resolve cycles or unknown dependencies before implementation. Preserve decisions and seams already confirmed in the spec. Ask the user only when scope, dependencies, or a public test seam remains unsettled.

## 2. Resolve TDD before writing tests

On Codex, load the registered Matt Pocock skill `mattpocock-skills:tdd` and its local resources. On Gemini CLI, activate `tdd` through the skill tool. Apply it at the public seams agreed in the plan. When delegating, pass each implementer the TDD instructions or the host-discovered resource paths, the agreed seam, and the standards.

If TDD is missing or disabled, name it and pause implementation. On Codex, run `codex plugin marketplace add mattpocock/skills` and `codex plugin add mattpocock-skills@mattpocock`. On Gemini CLI, clone upstream with `git clone https://github.com/mattpocock/skills.git mattpocock-skills` and run `gemini skills install ./mattpocock-skills/skills/engineering`. Use an existing upstream checkout if available. Reopen the session and confirm discovery before continuing.

## 3. Implement and verify

Work in dependency order. Parallelize disjoint task groups only when delegation and isolated worktrees are available. Integrate them one at a time and rerun affected checks. At each seam, run the failing test first, implement enough to pass, and re-run the targeted suite. Keep requirement and test evidence together. Obtain the user's decision before implementing a conflicting or materially changed requirement.

Use Codework's `refactor` for a scoped cleanup where warranted. Give it a clean phase worktree, a local implementation commit containing only the selected change, and the pinned comparison base. Use an isolated worktree for that candidate if the original checkout has unrelated tracked work. Ask it to preserve behavior and keep the work local.

Run the repository's coverage command on the candidate and pinned base when available. Record total and changed-line coverage and map gaps and public end-to-end scenarios to acceptance criteria. Ask which gaps to close and agree any new seams before adding tests. Demonstrate each added test can fail at its public seam and passes on the restored candidate. Consider unit, functional, fuzz, mutation, and chaos checks where they address relevant risks or repository requirements. Record reasons for omissions.

Run the exact quality-gate commands from `specs/tech-stack.md`, plus applicable more specific repository commands. Capture the command, revision, and result for every criterion and gate as passed, failed, unavailable, or inapplicable. Update the selected phase's `validation.md` with the evidence and check off criteria only when verified. Reproduce suspected pre-existing failures on the pinned base when possible. Record evidence for a failure or an unavailable check and leave any required gate outstanding. A waiver requires an explicit user decision and remains visible in the report.

## 4. Review and request human approval

Follow [the review instructions](references/review.md). Verify and address findings, then repeat affected tests and required gates on the revised work. If review cannot run, leave it pending and provide the handoff.

Present the branch and exact commit or base plus working diff and new-file hashes, requirement-to-test evidence, gate results, independent findings and dispositions, and open items. Ask for explicit approval of that revision. A request for changes returns the affected items to implementation, verification, and review, then comes back for fresh approval. Recheck that the revision still matches before acting on an approval.

The approved completion change may mark the selected roadmap phase `done` once required work and gates are satisfied. If that changes the reviewed tree, verify and present the new revision before publishing. Create or update a draft or ready PR only with the user's authorization, and confirm the remote head matches the approved revision before marking a PR ready.
