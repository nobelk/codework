---
name: constitution
description: Create or revise the project mission, tech stack and quality gates, and dependency-ordered roadmap in specs/. Confirm decisions with the user and prepare the documents for review.
license: Apache-2.0
---

# constitution

Read the [constitution workflow](references/workflow.md), then create or revise these repository documents.

- `specs/mission.md` defines the problem, users, measures, non-goals, and principles.
- `specs/tech-stack.md` defines engineering standards and the exact quality-gate commands later run by `code`.
- `specs/roadmap.md` sequences independently verifiable phases and marks the phase that reaches the minimum viable product. The `spec` skill uses its phase status and dependencies.

Survey the repository and any existing constitution. Resolve Matt Pocock's installed `grilling` skill and obtain decisions before writing. Follow the workflow's setup instructions if the skill is missing. Preserve stable phase IDs and existing decisions that still apply. Cross-check the documents before [independent review](references/review.md), or prepare a pending review handoff. Report the revision and disposition of findings, and leave the three files uncommitted.
