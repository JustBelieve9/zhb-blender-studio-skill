# Scene diagnostics

Run `studio.report()` first only when inspection is requested or needed for the
authorized task. It reports the active scene's objects and render properties;
resource counts and paths are file-wide. It does not evaluate all geometry,
re-bake simulations, compare duplicates or estimate render time.

Read the JSON fields: `scene`, `settings`, `scene_objects`, `datablocks`,
`resources`, `libraries`, `heavy_candidates`, `proxies`, `cache_note`.
Candidates such as subdivision level > 2, bump or displacement are reasons to
inspect, not automatically defects. Large textures may be necessary for output.

For a deeper requested report:

- Evaluate instances with the depsgraph, distinguishing unique meshes from
  per-instance triangle totals. State if expensive geometry was sampled.
- Check missing UDIM tiles and sequence members, not only the first file.
- Inspect external library paths relative to the library owning the datablock.
- Discover the scene's actual simulation providers. Use their documented cache
  validators when available; a file's existence is not a freshness test.
- Compare against requirements explicitly supplied for this project. There is
  no built-in Goodville, 1920², 100 mm or color-management canon.

Present the material findings and proposed next actions. Do not launch cleanup
because a report contains warnings.
