# Gateway Contract Release v0.6 Changelog

## v0.3

Introduced offline channel intake and Operational Registry handoff contracts.

## v0.4

Introduced adapter descriptors, delivery policy, runtime status and error taxonomy.

## v0.5

Introduced compatibility matrix, replay fixtures and dry-run delivery planner.

## v0.6

Packages accepted Gateway contracts into a stable offline release package for consumers.

Adds:

- release manifest;
- consumer bundles;
- consumer acceptance fixtures;
- backward compatibility gates;
- deprecation policy documentation;
- release and acceptance previews.

## Known non-live limitations

This release does not include live transport, production SDKs, DB writes, queues,
Redis, S3, runtime adapter calls, 1C writes, automatic posting or final price
calculation.

## Next allowed evolution

Next evolution should be approved by ForPrint System Blueprint.
