# Capability map

| Area | Shipped behavior | What is not claimed |
|---|---|---|
| Project setup | Helper: explicit resolution, FPS, frames, engine. Agent guidance: color/compositor and crop decisions. | No fixed studio look, preset library or general render-settings transfer tool. |
| Scene diagnostics | Helper: counts, settings, ordinary missing paths, heavy candidates and proxy state. | No evaluated triangle census, duplicate proof or simulation validation. |
| Cleanup | Agent procedures for exact duplicate checks, shared users and targeted unused IDs. | No automatic dedup/purge button or visual-equivalence guarantee. |
| Proxies | Helper: bounded PNG copies and restoration of local FILE textures. | No HDR/UDIM/sequence proxy conversion. |
| Variants | Agent procedures for separate files or explicit drivers. | No installed UI, legacy Studio variant migration or render queue. |
| Collect | Helper: new `.blend`, resources, manifest, extras, fresh-open path check. | No linked-library packaging, exhaustive third-party dependency discovery or cache freshness claim. |

Not included: autosave timers/snapshot management, permanent viewport overlays,
shader conversion, relink search, Draft/Final rendering, Sample Test, Frame
Analysis, Camera Rig, animation, physics, crowds, asset-library administration
or After Effects export. These are not prerequisites.

The package is a reusable agent skill with helper scripts, not a Blender extension
and not a complete replacement for every historical zhb Studio function.
