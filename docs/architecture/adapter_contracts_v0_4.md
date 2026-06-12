# Gateway v0.4 Adapter Contracts

Gateway v0.4 defines adapter-readiness contracts only.

It does not enable live runtime integrations.

## Purpose

Adapter contracts describe how future adapters may exchange normalized envelopes with Gateway and business modules.

## Supported directions

```text
inbound_channel_to_gateway
gateway_to_business_module
business_module_to_gateway
gateway_to_channel

Supported modules
telegram_bot
website
forprint_crm
mobile_app
forprint_integration_gateway
forprint_operational_registry
calculator_engine
forprint_prepress_hub
forprint_accounting_registry_service
forprint_library
Boundary

Gateway does not own:

client accounts
orders
accounting records
warehouse stock
canonical products/materials
final price calculation
production runtime
Runtime policy

All descriptors are offline/contract-only.

No descriptor may set:

live_enabled: true
queue_worker_enabled: true
external_runtime_calls_enabled: true