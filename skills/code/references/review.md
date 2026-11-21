# Implementation review

Give a separate read-only subagent, or a different model in a separate read-only session, the pinned base, exact candidate revision or diff and new files, source spec, task dependencies, acceptance criteria, repository standards, and evidence. Ask for numbered findings with severity, file and line, failing scenario, and violated requirement or standard. Ask for two passes.

1. **Spec compliance:** every requirement is implemented, excluded scope stays excluded, acceptance criteria match the tests, and the agreed seams cover normal, failure, and boundary behavior.
2. **Independent code review:** check correctness, regressions, architecture, integration, test strength, and the quality gates. Check that evidence refers to the candidate and that mandatory unavailable or failing checks are reported as outstanding.

Use a separate reviewer for each pass where available. Keep the reviewers read-only. If a separate reviewer or model is unavailable, give the user this packet and leave independent review pending. Verify each finding before acting and record its disposition. Give the reviewer the revised candidate for affected areas and include the final result in the approval packet.
