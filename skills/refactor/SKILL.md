---
name: refactor
description: Plan and apply a behavior-preserving refactor of a branch or pull request. Review architecture and readability, confirm the plan, and compare verification results.
license: Apache-2.0
---

# refactor

Read the [refactoring workflow](references/workflow.md). Pin the branch, comparison base, and baseline gate results. Use the [architecture](ARCHITECTURE.md) and [clean-code](CLEAN_CODE.md) references to examine the changed code and test boundaries.

Resolve Matt Pocock's installed `grilling` skill and follow the workflow's setup instructions if it is missing. Use it to confirm judgment calls and changes affecting observable behavior. Record the evidence, decisions, and ordered plan in `refactor-<id>.md`. Obtain [independent plan review](references/review.md) and obtain user approval before applying the reviewed plan. A pending review leaves a handoff.

Apply approved items in verifiable slices. Compare behavior and repository gate results at the baseline and candidate revisions. Leave the work local by default. If publication is requested, present the exact commits and PR payload for explicit approval before using the [PR helper](scripts/pr.py) or pushing.
