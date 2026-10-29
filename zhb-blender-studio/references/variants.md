# Variants without a permanently installed add-on

Use a copy-per-variant approach when a few deliverables differ substantially.
Record explicit differences, apply them in a separate process per copy and save
new `.blend` files. This is easier to reverse than a hidden driver network.

For many versions of one scene, a shared integer custom property such as
`scene["studio_variant"]` can drive object visibility and numeric values. Agree
variant names/indices first; preserve the index mapping and never renumber it
silently. Do not overwrite existing drivers, keyframes, constraints or expressions.

Create a `SINGLE_PROP` driver variable targeting the scene property. Expressions
like `v != 0` can control `hide_render`; numeric variants can use explicit
conditional expressions. Check each driven RNA path, array index and referenced
ID. Enum fields and material datablock pointers are not ordinary numeric driver
targets; use node switches/mixes or separate saved files where appropriate.

Visibility must account for the user's collections/view layers and intended
viewport behavior. A hidden collection can defeat object visibility drivers.
For a temporary preview record and restore the original variant and frame.

Verification: switch through every variant, update the depsgraph, inspect the
requested differences and unchanged shared parts, save/reopen the file and test
background evaluation. No GV Variants or Studio UI is installed by this skill.
Rendering/queues are outside this skill's scope.
