.PHONY: backend-test backend-lint backend-dev backend-device-demo backend-demo backend-generate-local

backend-test:
	cd services/backend && uv run pytest

backend-lint:
	cd services/backend && uv run ruff check .

backend-dev:
	cd services/backend && uv run uvicorn myth_forge_api.main:app --reload --port 8080

backend-device-demo:
	cd services/backend && uv run uvicorn myth_forge_api.main:app --host 0.0.0.0 --port 8080

backend-demo:
	cd services/backend && uv run uvicorn myth_forge_api.main:app --reload --port 8080

backend-generate-local:
	cd services/backend && uv run python -m myth_forge_api.cli generate-asset --provider local --prompt "Create a brass key relic worshiped by a tiny village."

.PHONY: backend-evaluate-3d backend-evaluate-npc backend-evaluate-local

backend-evaluate-3d:
	cd services/backend && uv run python -m myth_forge_api.cli evaluate-3d --provider local --suite default-v0 --output .local/3d-evaluation-local.json

backend-evaluate-npc:
	cd services/backend && uv run python -m myth_forge_api.cli evaluate-npc --provider local --suite default-v0 --tick-steps 2 --output .local/npc-evaluation-local.json

backend-evaluate-local: backend-evaluate-3d backend-evaluate-npc

.PHONY: backend-write-provider-env

backend-write-provider-env:
	@services/backend/scripts/write_backend_env.sh

.PHONY: final-apply-resources

final-apply-resources:
	@services/backend/scripts/apply_final_resources.sh

.PHONY: final-resources-preflight

final-resources-preflight:
	cd services/backend && uv run python -m myth_forge_api.cli final-resources-preflight --repo-root ../..

.PHONY: final-configured-preflight

final-configured-preflight:
	cd services/backend && uv run python -m myth_forge_api.cli final-configured-preflight --repo-root ../.. --output .local/final-configured-preflight.json

.PHONY: final-handoff-index

final-handoff-index:
	cd services/backend && uv run python -m myth_forge_api.cli final-handoff-index --repo-root ../.. --output .local/final-handoff-index.json

.PHONY: final-acceptance-local final-demo-launch final-rehearsal-local

final-acceptance-local:
	@services/backend/scripts/write_final_acceptance_local.sh

final-demo-launch:
	cd services/backend && uv run python -m myth_forge_api.cli final-demo-launch --mode local --repo-root ../.. --output .local/final-demo-launch-local.json

.PHONY: ios-deploy-runbook ios-deploy-runbook-local

ios-deploy-runbook:
	cd services/backend && uv run python -m myth_forge_api.cli ios-deploy-runbook --mode local --repo-root ../.. --output .local/ios-deploy-runbook-local.json

ios-deploy-runbook-local:
	@services/backend/scripts/write_ios_deploy_runbook_local.sh

final-rehearsal-local: backend-evaluate-local final-acceptance-local final-demo-launch ios-deploy-runbook-local

.PHONY: mobile-xcode-build

mobile-xcode-build:
	apps/mobile/ios/scripts/xcode_build_gate.sh

.PHONY: mobile-deploy-preflight

mobile-deploy-preflight:
	apps/mobile/ios/scripts/deploy_preflight.sh

.PHONY: mobile-write-deploy-config

mobile-write-deploy-config:
	apps/mobile/ios/scripts/write_deploy_local_config.sh
