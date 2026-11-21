# Independent review

Use a separate read-only subagent when the host and session permit delegation. Otherwise hand the packet to a different model in a separate read-only session. Include absolute artifact paths, the exact file hashes or Git revision under review, repository rules, source inputs, confirmed decisions, the focus below, and the check results. Ask for numbered findings citing a file and section or line, the consequence, and a suggested change. Keep edits and decisions in the calling session.

If neither review route is available, give the user the packet and mark independent review pending. If a report makes claims without showing which artifact it read, request a review with citations. Record the reviewer, revision, and findings or pending status. Recheck revised artifacts before reporting their status.

## Review focus

Review the plan against the frozen PR snapshot, head OID, related spec, and confirmed decisions. Check each in-scope thread is represented, classifications cite real evidence, proposed changes have a test seam, and proposed replies match planned work. Check that missing, resolved, and changed threads will be held before publication.
