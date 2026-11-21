---
name: design-doc
description: Create or revise a software design from requirements and repository evidence. Confirm open decisions, draw applicable C4 diagrams in Mermaid, and trace contracts, tasks, and ADRs to requirements.
license: Apache-2.0
---

# design-doc

Turn a PRD or other named requirements into a Markdown design. Read the [design workflow](references/workflow.md) and [template](assets/template.md). Ask for any explicitly named source that is inaccessible before drafting.

1. Read the PRD and project guidance and inspect the existing architecture. Resolve Matt Pocock's installed `grilling` skill before asking design questions. Follow the workflow's setup instructions if the skill is missing. Confirm open decisions with the user.
2. Keep the eight template sections. Use the [pattern guide](references/architecture-patterns.md) and [C4 Mermaid guide](references/c4-mermaid.md). Map stable requirement IDs to design sections, tasks, and verification. Put material decisions in linked ADRs.
3. Run `python3 <skill-dir>/scripts/check_design_doc.py <design>`. Report renderer availability separately from structural results. Obtain [independent review](references/review.md) or prepare a revision-specific handoff.
4. Leave the local design and ADRs uncommitted. Report the paths, evidence, and open decisions that affect the next spec.
