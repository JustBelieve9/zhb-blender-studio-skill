# Execution

Locate Blender from the user's environment; do not assume an OS or installation
path. Locate this skill relative to its own folder. Helpers use Blender's bundled
Python (`bpy`) and the standard library only. No pip installation is needed.

Background example; replace paths and quote them for the actual shell:

```text
blender --background project.blend --python-exit-code 1 --python /path/to/zhb-blender-studio/scripts/studio.py -- report --json /path/to/report.json
blender --background project.blend --python-exit-code 1 --python /path/to/zhb-blender-studio/scripts/studio.py -- prepare --width 1920 --height 1080 --fps 30 --save /path/to/prepared.blend
blender --background project.blend --python-exit-code 1 --python /path/to/zhb-blender-studio/scripts/studio.py -- proxies --max-px 1024 --save /path/to/proxy-work.blend
blender --background proxy-work.blend --python-exit-code 1 --python /path/to/zhb-blender-studio/scripts/studio.py -- restore-proxies --save /path/to/restored.blend
blender --background project.blend --python-exit-code 1 --python /path/to/zhb-blender-studio/scripts/studio.py -- collect --output /path/to/new-delivery --extra box3d_cache
```

Commands print `STUDIO_JSON ` followed by JSON. `--json` on report writes an
additional report file and refuses to overwrite it. Mutation helpers save only
to a new `--save` path and refuse the source/existing files. Parent directories
must exist. `collect` owns its own new output folder.

Live execution through any available Blender Python tool:

```python
import sys
sys.path.insert(0, "/path/to/zhb-blender-studio/scripts")
import studio
print(studio.report())
```

`report`, `prepare`, `make_proxies`, `restore_proxies` can be imported. Mutation
functions change in-memory data; the caller controls saving. Do not import/run
Collect in the user's GUI: it deliberately requires background mode.

Use `--factory-startup` only for independent scratch tests. A production scene
may require its existing profile for Geometry Nodes/simulation providers. Use
`--python-exit-code 1` so exceptions cause a failing shell status.

Do not construct shell text from untrusted names. Pass argument lists to
subprocess APIs. CLI `--help` must follow Blender's separator `--`.
