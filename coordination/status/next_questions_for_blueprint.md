# Next Questions for ForPrint System Blueprint — Integration Gateway after v0.5

## Module

`forprint_integration_gateway`

## Completed phase

`contract_compatibility_replay_dry_run_v0_5`

## Completed step

`gateway_contract_compatibility_ready`

## Questions

1. Should Gateway v0.6 extend dry-run compatibility into signed adapter contract manifests, or keep manifests deferred until real adapters are approved?

2. Should future Gateway prompts prioritize:
   - adapter manifest schema;
   - contract migration/version graph;
   - audit envelope hardening;
   - idempotency persistence design;
   - or cross-module compatibility pack generation?

3. Should any module-specific adapter remain explicitly blocked beyond v0.5?

4. Should Accounting Registry remain limited to accounting reference candidates until sanitized accounting samples and Blueprint approval are provided?

5. Should Mobile App remain planned/future until Calculator Engine and channel contracts are accepted as stable?