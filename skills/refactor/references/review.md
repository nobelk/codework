# Independent review

Use a separate read-only subagent when the host and session permit delegation. Otherwise hand the packet to a different model in a separate read-only session. Include absolute artifact paths, the exact file hashes or Git revision under review, repository rules, source inputs, confirmed decisions, the focus below, and the check results. Ask for numbered findings citing a file and section or line, the consequence, and a suggested change. Keep edits and decisions in the calling session.

If neither review route is available, give the user the packet and mark independent review pending. If a report makes claims without showing which artifact it read, request a review with citations. Record the reviewer, revision, and findings or pending status. Recheck revised artifacts before reporting their status.

## Review focus

Read the repository's architecture guidance, the refactor plan, CLEAN_CODE.md, the spec when present, and the diff from the pinned merge base. Check diagnoses against cited code, remedy behavior at edge cases, preservation of public contracts, test seams, and ordering. Ask for a new review if the execution changes the plan's scope.
