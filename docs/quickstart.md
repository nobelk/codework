# Codework quickstart

Codework takes a change from an EARS product requirements document through design, implementation, independent review, and human approval. It also includes branch-rebase and GitHub review-response workflows.

Use Git and Python 3.10 or later. For design rendering, put Mermaid CLI (`mmdc`) on PATH, or allow the bundled checker to obtain it through `npx`. GitHub workflows also need `gh` authenticated to the relevant host. Reading a PR requires repository and PR read access. Publishing requires authorization to push the PR head and write PR comments, descriptions, or reviewer assignments as applicable.

## Codex

Use Codex CLI 0.171.0 for the verified local package path. Install Matt Pocock’s plugin first.

```sh
codex plugin marketplace add mattpocock/skills
codex plugin add mattpocock-skills@mattpocock
codex plugin marketplace add nobelk/codework --ref v0.1.0
codex plugin add codework@codework
```

For development, pass the absolute checkout path in place of `nobelk/codework --ref v0.1.0`. Start a fresh `codex` session in the target repository. Use the `$` picker to select `codework:design-doc`, and confirm `mattpocock-skills:grilling` and `mattpocock-skills:tdd` appear. Run `$mattpocock-skills:setup-matt-pocock-skills` once in each repository to record tracker, labels, and document destinations.

## Gemini CLI

Use Gemini CLI 0.70.0 with Node.js 20 or later. Enable Agent Skills and authenticate the model. Clone the prerequisite with Git and install each group from disk. Gemini CLI 0.70.0 can reject Git URL skill installs with a `GIT_CONFIG_SYSTEM` error. [Gemini CLI installation](https://geminicli.com/docs/get-started/installation/)

```sh
git clone https://github.com/mattpocock/skills.git mattpocock-skills
gemini skills install ./mattpocock-skills/skills/engineering
gemini skills install ./mattpocock-skills/skills/productivity
gemini extensions install https://github.com/nobelk/codework --ref=v0.1.0
```

If extension installation falls back to Git and hits the same error, clone the tagged source with `git clone --branch v0.1.0 https://github.com/nobelk/codework.git` and run `gemini extensions install ./codework`. For development use `gemini extensions link /absolute/path/to/codework`. Review the sources and approve Gemini's trust prompts for the folders you install from.

Open Gemini in your target repository. Run `/skills list` and check for `grilling`, `tdd`, and the eight entries below. Prompt `Use the setup-matt-pocock-skills skill to configure this repository` once per repo. When Gemini asks to activate a skill, approve that skill by name. To update the Matt Pocock dependency, pull the upstream checkout and reinstall both local groups.

## Skill catalog

Append the inputs to the prompt for your host. On Gemini CLI, use the prompt in chat.

| Skill | Codex | Gemini CLI | Input → expected output |
| --- | --- | --- | --- |
| Requirements | `$codework:prd` | `Use the prd skill` | Brief or existing PRD → `prod_req.md` with EARS requirements, assumptions, and open questions |
| Design | `$codework:design-doc` | `Use the design-doc skill` | PRD, repository, and decisions → `docs/design/<slug>.md`, C4 diagrams, requirement map, linked ADRs |
| Constitution | `$codework:constitution` | `Use the constitution skill` | Project context and decisions → local `specs/mission.md`, `specs/tech-stack.md`, and `specs/roadmap.md` |
| Spec | `$codework:spec` | `Use the spec skill` | Roadmap phase or selected task → `specs/<name>/{requirements,plan,validation}.md` with acceptance checks and agreed test seams |
| Implementation | `$codework:code` | `Use the code skill` | Phase spec or ticket → tested change, acceptance evidence, independent review, and approval request |
| Refactor | `$codework:refactor` | `Use the refactor skill` | Branch or PR and comparison base → reviewed plan, behavior-preserving edits, and before/after gate results |
| Rebase | `$codework:rebase` | `Use the rebase skill` | Current branch and target base → replayed local branch, reconciliation and gate report, restored work |
| Review response | `$codework:review-response` | `Use the review-response skill` | GitHub PR and mode → evidence-backed plan, or verified changes and explicitly approved publication |

If a required dependency is missing, enable or install it and restart the session. Codework pauses the dependent step and names the skill that needs setup. See the [worked verification scenarios](workflow.md) and [observed results](verification.md). [Matt Pocock’s installation guide](https://github.com/mattpocock/skills#installation-30-second-setup) · [Gemini skill activation](https://geminicli.com/docs/tools/activate-skill/) · [Codex plugin packaging](https://developers.openai.com/plugins/build/plugins)
