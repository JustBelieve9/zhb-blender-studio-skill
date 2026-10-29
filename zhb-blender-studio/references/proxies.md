# Reversible texture proxies

`proxies --max-px 1024` creates a sibling workspace folder next to the input
`.blend` and redirects eligible local FILE images to unique proxy PNGs. Source
paths are stored under `zhb_studio_original_v1`. Source textures are untouched.
Already-proxied, packed, linked, tiled, sequence, floating-point/HDR and non-file
images are skipped and reported. Use `--image NAME` repeatedly to limit scope.

Destination names include a hash of the absolute original path, preventing
same-basename collisions. The helper does not reuse/overwrite existing proxies:
each run gets its own folder. Color space/alpha settings on the working image
are preserved. This is a working-preview tool; PNG conversion is not a promise
of identical precision or final shading.

`restore-proxies` validates original files before switching paths back. It leaves
proxy files on disk. Restore before final delivery. If the project moved, stored
relative paths may no longer resolve: locate originals deliberately rather than
deleting recovery metadata. Exporting the proxy-work `.blend` to a different
directory remaps relative paths through Blender's save operation.

Verify size, color space and alpha mode after creation/restoration; inspect normal
maps and alpha cutouts visually in a real project before relying on them.
