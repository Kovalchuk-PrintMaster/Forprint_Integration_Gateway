# Gateway v0.5 Replay Fixtures

Gateway v0.5 adds offline replay fixtures.

Fixtures are split into:

golden
negative

Golden fixtures must produce dry-run plans that pass.

Negative fixtures must be blocked as expected.

Golden paths
telegram new order -> CRM intake
telegram new order -> Operational Registry handoff candidate
website price estimate -> Calculator quote preview dry-run
CRM client lookup -> Operational Registry lookup candidate
future mobile prepress request -> Prepress Hub planned-future dry-run
Negative paths
missing client identity -> validation error
unsupported target module -> routing/compatibility error
live delivery requested -> forbidden live delivery
wrong contract version -> incompatible contract version
Accounting Registry posting attempt -> blocked by policy
1C write attempt -> blocked by policy

Replay fixtures do not send data anywhere.