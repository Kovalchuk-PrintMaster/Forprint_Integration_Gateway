PYTHON=.venv_gateway/bin/python
PIP=.venv_gateway/bin/pip

.PHONY: install test lint format check smoke check-report clean

install:
	$(PIP) install --upgrade pip
	$(PIP) install -e ".[dev]"

test:
	$(PYTHON) -m pytest -q

lint:
	$(PYTHON) -m ruff check app tests scripts

format:
	$(PYTHON) -m ruff format app tests scripts

check: lint test

smoke:
	$(PYTHON) scripts/run_gateway_smoke.py

check-report:
	$(PYTHON) scripts/run_gateway_checks.py

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type d -name "*.egg-info" -prune -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -prune -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -prune -exec rm -rf {} +

# =============================================================================
# ForPrint governance alignment
# =============================================================================

.PHONY: status-report
status-report:
	@echo "== Integration Gateway status report =="
	@mkdir -p reports
	@printf '{\n' > reports/gateway_module_status.json
	@printf '  "module_name": "forprint_integration_gateway",\n' >> reports/gateway_module_status.json
	@printf '  "module_status": "active",\n' >> reports/gateway_module_status.json
	@printf '  "current_phase": "governance_alignment_v0_1",\n' >> reports/gateway_module_status.json
	@printf '  "boundary": "validation_normalization_routing_only_no_business_ownership"\n' >> reports/gateway_module_status.json
	@printf '}\n' >> reports/gateway_module_status.json
	@echo "📄 Module status report: reports/gateway_module_status.json"

.PHONY: blueprint-pull
blueprint-pull:
	git -C /srv/software_development/forprint-project/forprint_system_blueprint pull --ff-only

.PHONY: blueprint-check
blueprint-check:
	@test -d /srv/software_development/forprint-project/forprint_system_blueprint/coordination/global_policy
	@test -d /srv/software_development/forprint-project/forprint_system_blueprint/coordination/standards
	@test -f /srv/software_development/forprint-project/forprint_system_blueprint/coordination/module_policy/forprint_integration_gateway/module_policy.md || \
	 echo "WARN: Integration Gateway module policy file not found under expected Blueprint path."
	@echo "✅ Blueprint paths checked."

.PHONY: blueprint-sync-directives
blueprint-sync-directives:
	@echo "DEFERRED: Integration Gateway directive sync is not implemented yet."

.PHONY: coordination-check
coordination-check:
	@test -f coordination/status/current_status.yaml
	@test -f coordination/status/current_status.md
	@test -f coordination/prompts/index.yaml
	@test -f coordination/reports/index.yaml
	@test -f coordination/status/next_questions_for_blueprint.md
	@echo "✅ Coordination files exist."

.PHONY: coordination-fix
coordination-fix:
	@echo "DEFERRED: automatic Integration Gateway coordination fix is not implemented yet."

.PHONY: module-policy-check
module-policy-check: blueprint-check

.PHONY: governance-check
governance-check:
	@echo "== ForPrint Integration Gateway governance check =="
	$(MAKE) blueprint-pull
	$(MAKE) blueprint-check
	$(MAKE) blueprint-sync-directives
	$(MAKE) module-policy-check
	$(MAKE) coordination-check
	$(MAKE) status-report

.PHONY: blueprint-prompts-list
blueprint-prompts-list:
	$(MAKE) blueprint-pull
	@cat /srv/software_development/forprint-project/forprint_system_blueprint/coordination/outgoing_prompts/forprint_integration_gateway/index.yaml

.PHONY: blueprint-prompt
blueprint-prompt:
	$(MAKE) blueprint-pull
	$(PYTHON) scripts/read_blueprint_outgoing_prompt.py
