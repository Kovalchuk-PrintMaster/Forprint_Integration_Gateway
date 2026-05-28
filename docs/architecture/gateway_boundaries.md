# Gateway Boundaries

## Purpose

ForPrint Integration Gateway is the contract transport, validation, normalization,
routing, correlation and idempotency boundary for ForPrint modules and customer channels.

It is not a business brain.

## Gateway responsibilities

Gateway may handle:

- integration request envelope;
- integration response envelope;
- validation errors;
- route matching;
- local placeholder routing rules;
- correlation id;
- idempotency key;
- audit event envelope in future;
- security filter event envelope in future.

## Gateway must answer

> Is this request valid, safe, normalized, traceable, idempotent, and where should it go?

## Gateway must not answer

> What is the business decision?

Business workflow decisions belong to ForPrint CRM.

## Relationship with other modules

### ForPrint System Blueprint

The Blueprint is the architecture truth source.

Gateway must follow Blueprint boundaries and naming direction.

### ForPrint CRM

CRM owns business workflow orchestration and human-facing dashboard decisions.

Gateway may route commands to CRM, but must not become CRM.

### ForPrint Library

Library owns canonical catalogs, contracts, schemas, semantic registry, aliases and versioning.

Gateway may later consume contract definitions from Library, but must not own Library truth.

### Operational Registry

Operational Registry owns operational truth for clients, orders, tasks and statuses.

Gateway must not become an order database or client registry.

### Accounting Registry

Accounting Registry owns invoice, payment and 1C accounting truth.

Gateway must not own invoices or payment status.

### Calculator Engine

Calculator Engine owns quote drafts, price breakdowns, product configuration and material estimates.

Gateway must not calculate prices.

### Prepress Hub

Prepress Hub owns file preparation and prepress processing flow.

Gateway must not process design files.

### Customer channels

Telegram Bot, Website and future Mobile App are customer channels.

Gateway must stay channel-agnostic and use concepts such as:

- customer_channel;
- customer_channel_request;
- customer_action;
- customer_session;
- customer_notification.

Gateway must not hardcode Telegram-only or Website-only logic.

## v0.1 boundary

The first version intentionally includes only:

- Python package skeleton;
- envelope models;
- validation error model;
- routing rule model;
- simple validator;
- simple router;
- in-memory idempotency service;
- local placeholder routes;
- tests.

The first version intentionally excludes:

- production API;
- database;
- real integrations;
- queues;
- external partner integrations;
- business logic.