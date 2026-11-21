---
name: prd
description: Create or revise a product requirements document from a brief using EARS. Interview the user on outcomes, scope, and quality targets, then validate traceable requirements for the design.
license: Apache-2.0
---

# prd

Create or revise `prod_req.md`. Read the [requirements workflow](references/workflow.md), [EARS rules](references/ears.md), and [template](assets/template.md) before interviewing or drafting.

1. Find the brief, project rules, existing requirements, and evidence from the repository. Ask for an explicitly requested source when it is inaccessible.
2. Resolve Matt Pocock's `grilling` through the installed host's skill registry. Follow the setup instructions in the workflow if it is missing. Confirm product decisions before writing.
3. Trace measurable goals to user stories and stable EARS requirement IDs. Record verification methods, assumptions, constraints, and open questions.
4. Run `python3 <skill-dir>/scripts/check_prd.py <prd>` and adjudicate the output. Run the [independent review](references/review.md) or provide a pending handoff. Report the checked revision, findings, and issues that block design. Leave the artifacts uncommitted for the user.
