# Verification record

Codework `0.1.0`, verified from 2026-11-21 through 2026-11-23. The source was `nobelk/dotfiles@d5750fe4b01a5f5794cd92288fe3164be2ad7cbc`. The environment used Codex CLI `0.171.0`, Gemini CLI `0.70.0`, Node.js `26.13.0`, Python `3.14.4`, and Mermaid CLI `12.2.0`. Both hosts used Matt Pocock's skills at `abeeaf95660ba9e8b7c753eb38f441ca707a8823` (plugin version `1.3.2`).

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

The Codex runs used the existing Codex login in isolated profiles. The outer task sandbox blocked the nested CLI's shell with a socket permission error. The successful runs used an approved invocation outside that sandbox with Codex's own sandbox active. Gemini's built-in activation tool loaded all eight release skills plus `grilling` and `tdd` when invoked directly against the clean profile. The tool returned each skill's instructions and resources. A Gemini headless prompt exited with code 41 because the test profile had no Gemini authentication.

## Live Codex workflows

- **Line Count.** Starting from the [brief](../examples/line-count/brief.md) and the [scenario prompts](workflow.md#line-count-from-requirements-to-approval), the tagged plugin created the EARS PRD, design and ADR, three constitution documents, and the Phase 1 spec from the generated roadmap. The PRD checker passed. The design checker rendered all four generated diagrams when run outside the nested model sandbox. The released `code` skill opened upstream `tdd` and implemented the agreed fixture scope in two test-first batches. Its gates were `python3 -m compileall -q line_count.py tests` and `python3 -m unittest discover -s tests`. Both exited zero in order and all seven subprocess tests passed.
- **Independent review.** The host could not start its review subprocesses and produced a pinned handoff. Two separate reviewers checked requirements and engineering standards against the handoff at base `4989814bc36d49b526603f3bd894e476188bb501`. They verified all 12 hashes and the passing gates. The standards pass found no issues. The spec pass flagged the use of two red/green batches. Upstream TDD specifies one behavior per cycle. It also flagged the exact stdout-byte contract, which was exercised on Linux. Windows CRLF behavior was deferred.
- **Failed gate and change request.** In one copy, the skill ran the added required gate `python3 -c 'raise SystemExit(17)'`, recorded the failure, and left the phase incomplete. In a separate copy, the fixture operator requested a two-path CLI regression. The new test failed on a temporary mutation accepting an extra argument. The original command and all eight tests passed the two gates on the revised candidate. An independent reviewer verified the revised hashes and found no issues in the regression. Human approval of the eight-test revision is pending. The CLI and test file hashes begin `d7ed0a7a38e3` and `5c378182902a`.
- **Refactor.** The skill planned one failure-reporting helper and pinned the starting commit. An independent reviewer verified the plan at SHA-256 `51ac97147e143921a23a2187fe6d346e74689ad8aa32f7f774a7b3bf6babd1f4` and found no material issues. After the fixture operator approved that plan, the skill applied it locally. All nine subprocess cases matched exit status, stdout, and stderr before and after. Both gates passed at the baseline and after the refactor.
- **Rebase.** `origin/main` in the [rebase fixture](workflow.md#rebase-with-a-preserved-index) produced a conflict preview and a decision prompt for `render.sh`. After the fixture operator confirmed `mode=main,feature`, the skill replayed the branch in a writable copy because the nested sandbox protected the original `.git` directory. It reconciled `feature.md`, passed `sh verify.sh`, restored the staged, unstaged, untracked, and ignored changes, and left the local remote's feature tip unchanged.

Live Gemini model workflows and the approved publish flow on a real sandbox GitHub PR still need the [worked scenarios](workflow.md). GitHub denied creation of the private verification repository for the current token. The PR helper's fixture tests exercised its publish calls locally.

## Release and gallery

The published tag `v0.1.0` points to `f227df0ef8840bb8cd922ab6bb1e875fe94c5fa9`. The release includes `codework.tar.gz` with the manifest at the archive root. [Codework v0.1.0](https://github.com/nobelk/codework/releases/tag/v0.1.0)

- **Codex CLI** installed from the tagged Git marketplace with the [quickstart commands](quickstart.md) in a clean profile. The registry returned all eight Codework skills and the installed upstream prerequisites with no discovery errors.
- **Gemini CLI** installed from the same tagged release in a separate clean profile. Installation metadata reported `github-release` and `v0.1.0`. `gemini skills list` returned all eight skills and the installed upstream prerequisites. Both hosts' installed skill directories matched the tagged tree.
- **Gemini gallery** had no matching entry as of 2026-11-23 UTC. The public default branch contains the root manifest. GitHub rejected adding the `gemini-cli-extension` topic with HTTP 403 because the current token lacks repository Administration write access. After the topic is set, verify the manifest in GitHub code search and look for `nobelk/codework` in the gallery after the crawler runs. [Gemini gallery requirements](https://geminicli.com/docs/extensions/releasing/) · [Gallery index](https://geminicli.com/extensions.json)
