# Verification record

Codework `0.1.0`, verified on 2026-11-21. The source was `nobelk/dotfiles@d5750fe4b01a5f5794cd92288fe3164be2ad7cbc`. The environment used Codex CLI `0.171.0`, Gemini CLI `0.70.0`, Node.js `26.13.0`, Python `3.14.4`, and Mermaid CLI `12.2.0`. Both hosts used Matt Pocock's skills at `abeeaf95660ba9e8b7c753eb38f441ca707a8823` (plugin version `1.3.2`).

## Observed locally

| Check | Result |
| --- | --- |
| Shared package contents | Passed. Both manifests name Codework at the same version. The package check found exactly eight skill files and their required assets, valid frontmatter names, and working local references. |
| Codex local install and discovery | Passed in a fresh profile. `codex plugin marketplace add mattpocock/skills` and `codex plugin add mattpocock-skills@mattpocock` installed the upstream plugin. The same commands with the local Codework marketplace and `codework@codework` installed Codework. App-server `skills/list` returned all eight Codework skills, `mattpocock-skills:grilling`, `mattpocock-skills:tdd`, and the upstream setup skill with no discovery errors. |
| Gemini local install and discovery | Passed in a fresh profile. The upstream `gemini skills install <url> --path skills/engineering` command failed with `GIT_CONFIG_SYSTEM`. Installing the engineering and productivity groups from a Git checkout passed. `gemini extensions validate <checkout>` and `gemini extensions install <checkout>` passed from trusted test directories. `gemini skills list` returned all eight Codework skills plus `grilling`, `tdd`, and the upstream setup skill. |
| Codex missing dependency | Passed. In a profile containing only Codework, the design pilot read the fixture, paused before the interview, named `mattpocock-skills:grilling`, and returned both install commands and the instruction to reopen the session. |
| Design checker | Passed for the Line Count [design fixture](../examples/line-count/design.md). All eight sections were in order and both captioned, cited Mermaid diagrams rendered. An unterminated Mermaid block failed validation. |
| PRD checker | Passed for the Line Count [PRD fixture](../examples/line-count/prod_req.md) with three functional requirements, one non-functional requirement, valid EARS clauses, and complete trace links. The header-only requirement tables failed validation. |
| Rebase fixture | Passed with real Git and a local bare remote. The diverged branch conflicted in `render.sh`. Its gate failed until the feature doc matched the chosen resolution, then passed. A cached resolution left the index unmerged. Success and abort restored the staged, unstaged, untracked, and ignored changes. The stash retained both sides of ignored file-directory collisions. The remote feature tip stayed fixed. These runs drove Git commands directly. |
| PR helpers | Passed against the deterministic `gh` fixture. The dry run left state unchanged. Publishing on the expected head posted the chosen reply to a 64-bit comment ID and retried idempotently. An invalid batch produced no writes. The helper held edited and deleted threads, blocked a moved PR head, and preserved the PR description around its managed block. Both PR body helpers rejected incomplete block markers before writing. |
| Python and shell | The local `unittest` suite, Python compilation, and shell syntax checks passed. |

Local commands from the repository root:

```sh
python3 -m unittest discover -s tests -v
python3 -m compileall -q skills tests
sh -n examples/rebase/setup.sh
```

## Host invocation and distribution

For the Codex invocation checks, initialize a Git sandbox and copy the Line Count PRD to its root as `prod_req.md`. Use a fresh profile and the given input with `codex exec --ephemeral --sandbox read-only '$codework:<skill> <input>'`. Use a profile with Codework alone for the missing dependency case. These checks exercise the entry points and first decisions or input validation.

| Skill | Codex input and observed result | Gemini CLI |
| --- | --- | --- |
| `prd` | `Create a PRD from missing-brief.md.` Prompted for the missing named source before drafting. | Discovered. Live run pending authentication. |
| `design-doc` | `Read prod_req.md, load grilling, and ask the first design decision.` Opened the installed `grilling` instructions and asked about the Phase 1 scope. | Discovered. Live run pending authentication. |
| `constitution` | `Use prod_req.md for the constitution and ask the first decision.` Opened upstream `grilling` and asked what the MVP should deliver. | Discovered. Live run pending authentication. |
| `spec` | `Plan Phase 1 from specs/roadmap.md.` Prompted for the missing named roadmap. | Discovered. Live run pending authentication. |
| `code` | `Read the installed TDD skill and prod_req.md. Identify the required input and CLI test seam.` Opened `tdd` and its references, named the three spec inputs, and proposed a subprocess seam. | Discovered. Live run pending authentication. |
| `refactor` | `Plan a local refactor against missing-base.` Reported the unresolved base and the missing baseline evidence. | Discovered. Live run pending authentication. |
| `rebase` | `Verify missing-base before starting the rebase.` Reported that the target did not resolve and stopped before mutation. | Discovered. Live run pending authentication. |
| `review-response` | `Start in plan-only mode` in a sandbox without a PR or remote. Requested the full PR URL. | Discovered. Live run pending authentication. |

The Codex pilot and invocation checks used the existing Codex login in isolated profiles. The outer task sandbox blocked the nested CLI's shell with a socket permission error. The successful runs used an approved invocation outside that sandbox with Codex's read-only sandbox active. Gemini headless invocation exited with code 41 because the test profile had no Gemini authentication. The complete requirements-to-approval loop, the live rebase, and the approved sandbox PR publish flow still need the [worked scenarios](workflow.md) on both hosts.

## Release and gallery

The public repository uses the root extension manifest and Codework marketplace. Publish `v0.1.0` as a GitHub Release so Gemini CLI can install from the source archive. Verify both remote installation commands in the [quickstart](quickstart.md). For gallery indexing the default branch must contain the root manifest, the repository must have the `gemini-cli-extension` topic, and the gallery must find it on its next crawl. [Gemini extension release and gallery requirements](https://geminicli.com/docs/extensions/releasing/)
