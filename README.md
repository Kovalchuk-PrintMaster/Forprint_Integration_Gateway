# ForPrint Integration Gateway

`forprint_integration_gateway` is the ForPrint boundary layer for:

- integration request envelope handling;
- validation;
- normalization placeholder;
- routing;
- correlation context;
- idempotency boundary;
- response envelope standardization.

## Current status

Bootstrap development.

This module is intentionally small in v0.1.

## Gateway question

The Gateway answers:

> Is this request valid, safe, normalized, traceable, idempotent, and where should it go?

The Gateway must not answer:

> What is the business decision?

Business decisions belong to ForPrint CRM and business workflow modules.

## Explicitly not included in v0.1

- production API;
- database migrations;
- real CRM integration;
- real Calculator integration;
- real Accounting integration;
- real Prepress integration;
- async queues;
- external partner integrations;
- customer/order database;
- business workflow logic.

## Local development

```bash
cd /srv/software_development/forprint-project/forprint_integration_gateway

python3.11 -m venv .venv_gateway
source .venv_gateway/bin/activate

make install
make check