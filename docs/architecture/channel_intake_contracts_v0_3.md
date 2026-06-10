# Gateway v0.3 — Channel Intake Contracts

## Purpose

This document describes the offline channel intake contract foundation for
ForPrint Integration Gateway v0.3.

The purpose is to prepare Gateway for Telegram Bot, Website, CRM and future
Mobile App intake without enabling live production integrations.

## Supported channel sources

- `telegram_bot`
- `website`
- `forprint_crm`
- `mobile_app`

`mobile_app` is planned/future only. It is not an active runtime in v0.3.

## Supported request kinds

- `new_order_request`
- `order_clarification`
- `price_estimate_request`
- `client_lookup_request`
- `file_prepress_request`
- `manager_handoff_request`

## Main models

- `ChannelSource`
- `ChannelIntakeEnvelope`
- `ClientIdentityHint`
- `ContactHint`
- `BusinessRequestKind`
- `BusinessRequestPayload`
- `NormalizedGatewayRequest`
- `GatewayValidationIssue`
- `GatewayRouteDecision`
- `GatewayCorrelationContext`
- `GatewayIdempotencyPolicy`

## Validation boundary

Gateway validates only envelope-level structure:

- required fields exist;
- supported channel source;
- supported request kind;
- at least one client identity/contact hint exists.

Gateway does not validate:

- real business correctness;
- CRM workflow;
- final price;
- accounting document correctness;
- warehouse stock;
- canonical product/material schema.

## No live runtime

v0.3 does not add:

- production API;
- database;
- queues;
- Redis;
- S3;
- live Telegram calls;
- live Website calls;
- live CRM calls;
- live Operational Registry calls.

## Boundary

Gateway remains a validation, normalization, routing, idempotency and
correlation boundary.

Gateway must not become a business brain or schema source of truth.
docs/architecture/operational_handoff_contracts_v0_3.md
# Gateway v0.3 — Operational Handoff Contracts

## Purpose

This document describes offline Operational Registry handoff candidates for
ForPrint Integration Gateway v0.3.

Gateway may prepare handoff candidate objects, but it must not write to
Operational Registry or own operational data.

## Handoff candidate

The local model is:

- `OperationalRegistryHandoffCandidate`

It contains:

- candidate id;
- source intake id;
- target owner module;
- request kind;
- normalized summary;
- client identity hints;
- correlation context;
- route decision;
- payload snapshot;
- live write flag.

## Important rule

`is_live_write_enabled` must remain `false` in v0.3.

Gateway does not create:

- clients;
- orders;
- tasks;
- statuses;
- operational records.

## Ownership

Operational Registry remains the owner of:

- client registry;
- order registry;
- operational tasks;
- operational statuses.

Gateway only prepares offline handoff candidates for future integrations.