# Local GatewayProcessor Example

## Purpose

This document shows how to run the local v0.2 GatewayProcessor flow.

The flow is developer-only and does not start API, database, queue or real integrations.

## Run smoke scenario

```bash
make smoke

or directly:

.venv_gateway/bin/python scripts/run_gateway_smoke.py
Default example

The default smoke script loads:

examples/requests/customer_channel_quote_preview_request.json

It then:

loads local placeholder routes;
creates GatewayProcessor;
validates the request envelope;
checks idempotency;
matches route;
prints normalized IntegrationResponse.
Run another example request
.venv_gateway/bin/python scripts/run_gateway_smoke.py crm_to_calculator_quote_recalculation_request.json
.venv_gateway/bin/python scripts/run_gateway_smoke.py crm_to_accounting_invoice_request.json
Important boundary

The smoke runner does not call:

CRM;
Calculator Engine;
Accounting Registry;
Prepress Hub;
Website;
Telegram Bot;
Mobile App.

It only proves the local Gateway boundary pipeline.