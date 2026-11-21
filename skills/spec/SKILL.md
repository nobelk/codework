---
name: spec
description: Plan or revise a selected roadmap phase or task, with traceable requirements, ordered work, agreed public test seams, and a validation plan for implementation.
license: Apache-2.0
---

# spec

Read the [spec workflow](references/workflow.md) before planning. Select the requested task or a dependency-ready phase in `specs/roadmap.md`. Ask for an inaccessible or ambiguous input. Read the mission, standards, quality gates, and linked design and requirements.

Resolve Matt Pocock's installed `grilling` skill and confirm scope, decisions, and public test seams before drafting. Follow the workflow's setup instructions if the skill is missing.

Write `specs/<name>/requirements.md`, `plan.md`, and `validation.md`. Trace PRD requirement IDs and linked ADRs to dependency-ordered task groups and acceptance criteria. Record applicable verification commands and reasons to omit checks. Disposition [independent review](references/review.md) findings or report a handoff. Present the spec and review status for approval and pass its path to `code`.
