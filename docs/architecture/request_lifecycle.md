# Gateway Request Lifecycle

## Purpose

This document explains the local v0.2 request lifecycle for ForPrint Integration Gateway.

The Gateway remains a validation, routing, correlation and idempotency boundary.
It does not make business decisions.

## Lifecycle

```text
source module / customer channel
↓
IntegrationRequest
↓
SimpleValidator
↓
InMemoryIdempotencyService
↓
SimpleRouter
↓
IntegrationResponse
↓
source module / future adapter / audit context

Step 1 — Source request

A request may come from:

CRM;
customer channel;
future Website adapter;
future Mobile App adapter;
future internal module adapter.

In v0.2 there are no real adapters. Only local example payloads exist.

Step 2 — IntegrationRequest envelope

Gateway receives a normalized envelope with:

request_id;
correlation_id;
idempotency_key;
source_module;
source_channel;
target_module;
contract_id;
contract_version;
operation;
payload;
metadata;
created_at.
Step 3 — Envelope validation

Gateway validates only envelope-level structure.

Allowed in v0.2:

required envelope field exists;
required envelope field is not empty;
payload is a dictionary;
metadata is a dictionary.

Not allowed in v0.2:

deep payload schema validation;
business rule validation;
Calculator price validation;
CRM workflow validation;
Accounting document validation.
Step 4 — Idempotency check

Gateway checks idempotency_key using an in-memory service.

This is not persistent and not production-ready.

The goal is to prove the boundary behavior without adding a database.

Step 5 — Routing

Gateway matches a local placeholder route by:

source_module;
target_module;
contract_id;
operation.

Gateway does not call the target module in v0.2.

Step 6 — IntegrationResponse

Gateway returns a standardized response envelope.

Possible current statuses:

routed;
validation_failed;
duplicate_ignored;
route_not_found.
Boundary

Gateway must not become:

business brain;
CRM;
Operational Registry;
Library;
Accounting Registry;
Calculator;
Prepress Hub;
customer/order database;
schema source of truth.

Canonical contract/schema truth belongs to ForPrint Library in the future.