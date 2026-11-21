# Independent review

Use a separate read-only subagent when the host and session permit delegation. Otherwise hand the packet to a different model in a separate read-only session. Include absolute artifact paths, the exact file hashes or Git revision under review, repository rules, source inputs, confirmed decisions, the focus below, and the check results. Ask for numbered findings citing a file and section or line, the consequence, and a suggested change. Keep edits and decisions in the calling session.

If neither review route is available, give the user the packet and mark independent review pending. If a report makes claims without showing which artifact it read, request a review with citations. Record the reviewer, revision, and findings or pending status. Recheck revised artifacts before reporting their status.

## Review focus

Review the delta from the pinned new base to the candidate revision. Check conflicts against both sides' intent, range-diff mismatches, semantic reconciliation, and code, test, spec, and documentation consistency. Include the conflict list and the two reconciliation reports in the packet. Review the committed delta before restoring unrelated local work.
