# Gateway v0.4 Error Taxonomy

Gateway v0.4 defines structured error categories for adapter-readiness.

## Required categories

```text
validation
routing
idempotency
correlation
adapter_availability
forbidden_live_delivery
unsupported_module
boundary_violation
external_runtime_disabled
malformed_envelope
incompatible_contract_version

Each error has:

code
category
severity
retryable
message
metadata

The taxonomy is an offline fixture only.

It does not trigger runtime retries, queues, external calls, or automatic delivery.


## `docs/architecture/gateway_delivery_policy_v0_4.md`

```markdown id="xsji18"
# Gateway v0.4 Delivery Policy

Gateway v0.4 delivery policy is offline-only.

## Delivery modes

```text
offline_fixture_only
manual_preview_only
dry_run_only
future_live_adapter
forbidden

Default safe delivery mode:

offline_fixture_only
Runtime status values
planned
contract_ready
dry_run_ready
blocked
forbidden

No adapter is live.

Retry policy descriptors
no_retry
manual_review
retry_when_runtime_adapter_exists
blocked_until_blueprint_approval

Retry policies are descriptors only.

Gateway v0.4 does not implement:

queue workers
real retry execution
Redis
S3
external API calls
runtime adapter calls
Accounting Registry restriction

The Accounting Registry adapter must keep:

automatic_posting_allowed: false
one_c_write_allowed: false
live_enabled: false
Mobile App restriction

Mobile App remains planned/future and must not be marked live.


---