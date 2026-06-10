# Gateway v0.3 — Operational Handoff Contracts

## Purpose

This document describes offline Operational Registry handoff candidates for
ForPrint Integration Gateway v0.3.

The Gateway may prepare handoff candidate objects, but it must not write to
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

## Current v0.3 scope

Allowed:

- offline handoff candidate fixtures;
- local dataclass model;
- local preview output;
- tests that confirm live writes are disabled.

Not allowed:

- production Operational Registry API calls;
- direct database writes;
- migrations;
- queue producers/consumers;
- live task creation;
- live client creation;
- live order creation.

## Boundary confirmation

ForPrint Integration Gateway remains a validation, normalization, routing,
idempotency and correlation boundary.

It must not become the owner of operational truth.