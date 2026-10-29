# Prepare a project

`prepare` supports explicit width, height, FPS, first/last frame and engine
(`CYCLES`, `BLENDER_EEVEE`, `BLENDER_WORKBENCH`). Unspecified fields stay as they
are. Fractional FPS is represented through `fps` and `fps_base`.

For color management, samples, output format and compositor, the agent reads
the actual Blender properties, proposes the requested values and applies only
those values. Preserve user node graphs and artist-tuned lights/worlds. Appending
foreign compositor templates may also append unwanted scenes: inspect references.

Transferring settings between scenes is not included in the helper. If explicitly
requested, first enumerate the selected property groups and compare source/target
before implementing a scene-specific transfer. Do not copy the whole scene blindly.

Crop guides: for an explicitly chosen master and target sizes, compute centered
rectangles and their intersection. A composited guide is visible in output;
camera viewport guides are not. Ask which is intended when ambiguous. Do not
silently embed a grid in final images. No grid image or draw handler is bundled.
