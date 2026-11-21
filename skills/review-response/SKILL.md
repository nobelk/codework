---
name: review-response
description: Plan responses to GitHub pull request review threads or implement approved changes. Verify replies against the reviewed revision and obtain approval before publishing.
license: Apache-2.0
---

# review-response

Read the [review response workflow](references/workflow.md) and use the [GitHub helper](scripts/pr.py). Load the PR and freeze its head and thread snapshot. Read the flagged code at that head, relevant tests, and available spec or ticket evidence.

Resolve Matt Pocock's installed `grilling` skill before confirming disputed classifications, scope, or replies. Follow the workflow's setup instructions if the skill is missing. Write the evidence-backed plan and drafts in `review_response_<n>.md`. Obtain an [independent plan review](references/review.md) or report the review handoff. In plan-only mode deliver the local plan with no publication.

In execute mode apply agreed changes, verify the candidate against repository gates, and make sure every proposed reply describes the actual change. Ask for explicit approval of the head, push destination, exact replies, PR body update, and reviewer requests before sending. Use the helper's expected-head check and original thread versions. Hold changed threads and report posted, held, and failed items.
