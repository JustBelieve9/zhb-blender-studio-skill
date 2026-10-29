---
name: zhb-blender-studio
description: "Prepare, inspect, clean and package Blender projects for handoff. Use for scene diagnostics, duplicate cleanup, reversible texture proxies, scene variants and Collect requests; not for modeling, animation or rendering."
license: MIT
metadata:
  author: JustBelieve9
  version: "0.1.0"
---

# ZHB Studio

Work with the user's Blender project as a studio pipeline assistant. Reply in the
user's language. This skill is standalone: no zhb add-on, Core library, companion
skill or specific MCP server is required. Blender 5.2 is the tested baseline.

## Choose the operation

| Request | Read when needed | Included helper |
|---|---|---|
| Inspect a scene, find missing resources or heavy data | [diagnostics.md](references/diagnostics.md) | `scripts/studio.py report` |
| Set resolution, FPS, frame range or engine | [prepare.md](references/prepare.md) | `scripts/studio.py prepare` |
| Find/merge duplicates or remove unused data | [cleanup.md](references/cleanup.md) | Agent workflow; no automatic merge helper |
| Make smaller textures or restore originals | [proxies.md](references/proxies.md) | `scripts/studio.py proxies` / `restore-proxies` |
| Make versions of a scene | [variants.md](references/variants.md) | Agent workflow; no installed UI |
| Collect a project and its resources | [collect.md](references/collect.md) | `scripts/studio.py collect` |

For tools, arguments and execution modes read [execution.md](references/execution.md).
For the precise feature boundary read [features.md](references/features.md).

## Preserve project intent

- Inspect the target scene, saved file path and available Blender version first.
  Do not impose project-specific resolution, lens, duration, look or engine.
- Diagnosis is read-only. Run only the requested operation; a report does not
  authorize cleanup. State whether scope is one scene or the whole file.
- Before changing shared data, enumerate affected users. Save a recoverable copy
  before batch cleanup, driver creation or replacement of existing settings.
  Saving must follow the user's output choice; never overwrite a source by default.
- Prefer the data API; discover actual RNA properties/enums rather than copying
  obsolete API examples. Find nodes by type/identifier, not translated UI names.
- For analysis of evaluated meshes, release temporary meshes in `finally`.
  Restore frame, selection and temporary state after inspections.
- Do not delete Text datablocks as cleanup. Do not merge resources because names,
  previews or rounded values look similar. Proxy paths must remain reversible.
- For Collect use a fresh background process on the saved project. The included
  helper rejects linked libraries and missing resources; do not bypass that refusal
  silently. Unknown simulation caches require an explicit resource inventory.
- Use the user's existing execution profile when scene evaluation needs add-ons.
  Do not install, enable, remove or reconfigure add-ons to run this skill.

## Verify what changed

Compare the requested properties, affected data counts and resulting files. For
visual changes inspect representative frames; record when no visual review ran.
For a collected project reopen the copy, check paths, then test after hiding the
source folder if full independence is required. Opening it while original paths
remain accessible alone does not prove portability.

Report the output path, concrete changes, performed checks and remaining external
dependencies. A successful process exit is not proof of visual equivalence or
simulation freshness. Report unknown cache formats as unverified, not ready.

## Extend from real cases

Use [cases.md](references/cases.md) when a user supplies a new production example.
Record reproducible inputs and expected results before generalizing its settings.
Do not turn a single project's preferences into new global defaults.
