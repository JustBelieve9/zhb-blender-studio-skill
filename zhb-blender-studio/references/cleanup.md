# Deliberate cleanup

This is an agent workflow, not an automatic merge script. Start with a proposed
plan containing resource type, exact names, users, proposed survivor and reason.
Work in a saved copy. Restrict the operation to the agreed resource scope.

## Duplicate candidates

Names with `.001` are only candidates. For images compare original bytes plus
color space, alpha mode, source mode and usage. Ignore different file paths as
an equality criterion. For meshes compare exact coordinates/topology, edges,
polygon boundaries, UVs, normals where relevant, all attributes and their values,
material slots/indices and shape keys. Skip animated or linked data unless its
semantics are explicitly understood. For materials and node groups compare node
settings, exact socket values, links by node identity, group interfaces and nested
dependencies. Matching node types alone does not establish matching topology.

If exact equivalence cannot be established, keep the resources separate. Never
round values to force a match. If implementing a reusable fingerprint later,
test non-equivalent graphs/meshes as well as identical examples.

Once the user has authorized the concrete cleanup scope, remap users and remove
only verified duplicates. Compare user counts and representative renders. Do not
convert mesh instances into independent copies accidentally.

## Unused data

List zero-user IDs first. Preserve Text blocks, intentionally kept assets,
fake-user data, linked data and user-selected exclusions. A broad recursive
`orphans_purge()` is not an acceptable substitute for a targeted list when Text
preservation matters. Recheck users immediately before each removal.

Shader simplification and Principled-to-Diffuse replacement are not bundled
operations. They change the look and need an explicit visual target, separate
implementation and before/after review.
