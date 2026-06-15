# Gateway v0.6 Contract Release Package

Gateway v0.6 packages accepted Gateway contract layers into a stable offline
contract release.

The package includes:

```text
channel_intake
adapter_contracts
error_taxonomy
delivery_policy
compatibility_matrix
dry_run_delivery_planner
replay_fixtures
consumer_acceptance

The release package is stored under:

contracts/gateway/v0_6/

It does not enable runtime transport, live APIs, database writes, queues, Redis,
S3, 1C writes, automatic posting, final price calculation or production SDKs.