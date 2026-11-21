# Ticket input

Use the issue tracker named in the repository guidance or the user's prompt. Read the parent spec and its relevant child items, acceptance criteria, and blocker links before planning. Confirm missing or inaccessible content with the user. Keep the evidence linked to the original IDs.

| Input | Read with | Dependencies and trace |
| --- | --- | --- |
| GitHub | Authenticated `gh issue view` or configured GitHub tools | Use native sub-issue and blocker links or explicit blocking text. Link issues in an approved PR. |
| Jira | Configured Jira tools, or user-provided issue text | Use the issue links and preserve the keys in the spec and PR. |
| Local | The supplied spec and ticket files, such as `.scratch/<feature>/issues/` | Use explicit blocked-by references. Pass absolute paths when files live outside a phase worktree. |

Build the same task graph as for a `spec` input. Record each ticket's public test seam and confirm any unsettled seams with the user. Where the ticket does not name repository standards, use `specs/tech-stack.md`, CI, and repository guidance. Detect missing dependencies and cycles before implementation. Seek approval for tracker writes, status transitions, or PR publication.
