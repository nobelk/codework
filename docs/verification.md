# Verification record

Codework candidate `0.1.0`, verified locally on 2026-11-21. Source is `nobelk/dotfiles@d5750fe4b01a5f5794cd92288fe3164be2ad7cbc`. The local test environment used Codex CLI `0.171.0`, Python `3.14.4`, and a cached Matt Pocock plugin `1.3.2` at Git revision `abeeaf95660ba9e8b7c753eb38f441ca707a8823`. Gemini CLI target `0.70.0` remains unverified.

## Observed locally

| Check | Result |
| --- | --- |
| Shared package contents | Passed. Both manifests name Codework at the same version. The package check found exactly eight skill files and their required assets, valid frontmatter names, and working local references. |
| Codex local install and discovery | Passed. In a fresh Codex configuration, `codex plugin marketplace add <marketplace-root>` and `codex plugin add codework@codework` installed the candidate. The same commands with the local upstream snapshot registered the pre-existing Matt Pocock package. Codex app-server `skills/list` returned all eight namespaced Codework skills, `mattpocock-skills:grilling`, `mattpocock-skills:tdd`, and the upstream setup skill with no discovery errors. |
| Codex missing dependency discovery | Passed at the registry level. After removing the upstream plugin from the isolated profile, Codex still returned the eight Codework skills and omitted the upstream entries. The agent's missing-dependency response remains unverified. |
| Design pilot invocation | Codex accepted `$codework:design-doc read prod_req.md, resolve grilling, and ask the first design decision.` and started a turn. The model connection failed, so it produced no interview or design. The supplied design fixture passed the eight-section and two-figure structural checks. The checker reported renderer unavailable because `mmdc` was absent. |
| PRD checker | Passed for the Line Count [fixture](../examples/line-count/prod_req.md) with three functional requirements, one non-functional requirement, valid EARS clauses, and complete trace links. |
| Rebase fixture | Passed with real Git and a local bare remote. The diverged branch conflicted in `render.sh`. Its gate failed until the feature doc matched the chosen resolution, then passed. Success and abort restored the staged, unstaged, untracked, and ignored changes. The stash retained both sides of ignored file-directory collisions. The remote feature tip stayed fixed. These runs drove Git commands directly. |
| Review-response helper | Passed against the deterministic `gh` fixture. The dry run left state unchanged. The expected-head publish posted the chosen reply to a 64-bit comment ID and retried idempotently. An invalid batch produced no writes. The helper held edited and deleted threads, blocked a moved PR head, and preserved the PR description around its managed block. |
| Python and shell | The local `unittest` suite, Python compilation, and shell syntax checks passed. |

Local commands from the repository root:

```sh
python3 -m unittest discover -s tests -v
python3 -m compileall -q skills tests
sh -n examples/rebase/setup.sh
```

## Host invocation and distribution

| Skill | Codex CLI | Gemini CLI |
| --- | --- | --- |
| `prd` | Discovered. Fixture checker ran directly. Live invocation pending. | Installation, discovery, and live invocation pending. |
| `design-doc` | Discovered. Explicit invocation started. The model connection failed. Fixture structure passed with rendering unverified. | Installation, discovery, and live invocation pending. |
| `constitution` | Discovered. Three-file workflow pending. | Installation, discovery, and live invocation pending. |
| `spec` | Discovered. Generated-roadmap handoff pending. | Installation, discovery, and live invocation pending. |
| `code` | Discovered. Live TDD, gate, and approval cycle pending. | Installation, discovery, and live invocation pending. |
| `refactor` | Discovered. Live plan and behavior comparison pending. | Installation, discovery, and live invocation pending. |
| `rebase` | Discovered. Direct fixture passed. Live workflow pending. | Installation, discovery, and live invocation pending. |
| `review-response` | Discovered. Helper fixture passed. Live sandbox PR pending. | Installation, discovery, and live invocation pending. |

The sandbox blocked Codex model-service connections, GitHub Git transport, and npm registry resolution. Gemini CLI and Mermaid CLI were absent. Clean installs from GitHub, model-driven interviews and implementation, independent reviews and human approvals of the example on both hosts, and live GitHub side effects remain pending. The [worked scenarios](workflow.md) give the prompts, fixtures, and expected observations for those checks.

## Release and gallery

The repository is public. The candidate includes the root Gemini extension manifest. Release and gallery publication are pending. The Git push dry run failed to resolve GitHub, and the GitHub CLI topic update could not connect to the API. From the release revision, publish tag `v0.1.0`, set the repository topic `gemini-cli-extension`, and verify both remote installation commands in the [quickstart](quickstart.md). The Gemini gallery indexes eligible tagged repositories daily. Record the actual tag, published revision, install results, and gallery listing when they are available. [Gemini extension release and gallery requirements](https://geminicli.com/docs/extensions/releasing/)
