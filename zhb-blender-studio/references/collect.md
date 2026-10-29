# Collect: a new delivery folder

Use the saved source file in a fresh background process. The helper creates a
new directory containing the original `.blend` filename, `resources/`, optional extra caches and
`manifest.json`. It never saves over the source. Existing destinations are refused.

Before running, identify simulation providers, caches and linked libraries. The
generic helper cannot infer provider-specific cache freshness. Re-bake/validate
using available provider tools if the delivery requires it. No zhb Core import
is attempted. Recipients still need any add-ons required by the scene.

Supported: local images, sounds, fonts, movie clips, cache-file IDs and volumes
with ordinary file paths; image UDIM tiles and numbered image sequences;
already packed resources remain packed. Unpacked movie-clip/volume sequences
are rejected because copying only one member would produce an incomplete result.
Linked libraries are rejected rather than left as hidden source dependencies.
The agent can separately localize a copy if the user wants that tradeoff.

Extra file/folder resources use repeated `--extra relative/path`. These must stay
inside the source project directory; they retain the same relative locations in
the delivery. Include e.g. `box3d_cache` or explicitly identified sidecar caches.
Reject symlinks/junctions. A provider that derives cache names from the `.blend`
filename needs deliberate renaming/configuration after the copy, not a blind extra.

Before any copying, all planned resource paths are validated. Then a unique
staging folder is populated, active proxy paths are restored in memory, copied
paths are rewritten relative to the new `.blend`, and an independent Blender
opens the staged copy to validate paths. Failed staging folders are retained
for inspection and named in the error. Successful staging is renamed to the
requested destination; no user data is deleted on failure.

`manifest.json` records resources and hashes, extras, verification, and unknown
cache freshness. No purge, dedup or shader changes happen during Collect.

The fresh-open check proves supported paths resolve at that moment. For a strict
handoff test, reopen after temporarily making the source folder unavailable and
run the scene's real provider checks. Keep the report honest about unsupported
custom node paths, custom properties and third-party cache formats.
