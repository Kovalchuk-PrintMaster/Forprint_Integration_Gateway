# Gateway v0.5 Dry-run Delivery Planner

Gateway v0.5 adds a dry-run delivery planner.

The planner builds delivery plans without sending anything.

Each plan includes:

source module
target module
operation
contract version
delivery mode
runtime status
live delivery enabled false
idempotency key
correlation id
compatibility result
boundary flags
planned steps
expected owner module
error result if blocked

The planner does not implement:

live API
database writes
queues
Redis
S3
external API calls
runtime adapter calls
1C writes
automatic posting
final price calculation