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

.PHONY: visual-regression visual-regression-local

visual-regression:
	cd services/backend && uv run python -m myth_forge_api.cli visual-regression --repo-root ../..

visual-regression-local:
	cd services/backend && uv run python -m myth_forge_api.cli visual-regression --repo-root ../.. --output .local/visual-regression-local.json

.PHONY: backend-evaluate-3d backend-evaluate-npc backend-evaluate-local

backend-evaluate-3d:
	cd services/backend && uv run python -m myth_forge_api.cli evaluate-3d --provider local --suite default-v0 --output .local/3d-evaluation-local.json

backend-evaluate-npc:
	cd services/backend && uv run python -m myth_forge_api.cli evaluate-npc --provider local --suite default-v0 --tick-steps 2 --output .local/npc-evaluation-local.json

backend-evaluate-local: backend-evaluate-3d backend-evaluate-npc

.PHONY: backend-write-provider-env

backend-write-provider-env:
	@services/backend/scripts/write_backend_env.sh

.PHONY: provider-handoff

provider-handoff:
	cd services/backend && uv run python -m myth_forge_api.cli provider-handoff --require-core-real --output .local/provider-handoff.json

.PHONY: final-apply-resources

final-apply-resources:
	@services/backend/scripts/apply_final_resources.sh

.PHONY: final-resource-init

final-resource-init:
	cd services/backend && sh scripts/init_final_resources.sh

.PHONY: final-resources-preflight

final-resources-preflight:
	cd services/backend && uv run python -m myth_forge_api.cli final-resources-preflight --repo-root ../.. --output .local/final-resources-preflight.json

.PHONY: final-resource-requirements

final-resource-requirements:
	cd services/backend && uv run python -m myth_forge_api.cli final-resource-requirements --repo-root ../.. --output .local/final-resource-requirements.json

.PHONY: final-resource-apply-preview

final-resource-apply-preview:
	cd services/backend && uv run python -m myth_forge_api.cli final-resource-apply-preview --repo-root ../.. --output .local/final-resource-apply-preview.json

.PHONY: final-resource-repair-preview final-resource-repair

final-resource-repair-preview:
	cd services/backend && uv run python -m myth_forge_api.cli final-resource-repair-preview --repo-root ../.. --output .local/final-resource-repair-preview.json

final-resource-repair:
	cd services/backend && uv run python -m myth_forge_api.cli final-resource-repair --repo-root ../.. --output .local/final-resource-repair.json

.PHONY: final-resource-fill-guide

final-resource-fill-guide:
	cd services/backend && uv run python -m myth_forge_api.cli final-resource-fill-guide --repo-root ../.. --output .local/final-resource-fill-guide.json --markdown-output .local/final-resource-fill-guide.md

.PHONY: final-external-action-ledger

final-external-action-ledger:
	cd services/backend && uv run python -m myth_forge_api.cli final-external-action-ledger --repo-root ../.. --output .local/final-external-action-ledger.json

.PHONY: final-launch-closure-packet

final-launch-closure-packet:
	cd services/backend && uv run python -m myth_forge_api.cli final-launch-closure-packet --repo-root ../.. --output .local/final-launch-closure-packet.json

.PHONY: local-showcase-smoke

local-showcase-smoke:
	cd services/backend && uv run python -m myth_forge_api.cli local-showcase-smoke --output .local/local-showcase-smoke.json

.PHONY: final-local-report-refresh final-local-report-refresh-local

final-local-report-refresh:
	cd services/backend && uv run python -m myth_forge_api.cli final-local-report-refresh --repo-root ../.. --output .local/final-local-report-refresh.json

final-local-report-refresh-local:
	@services/backend/scripts/write_final_local_report_refresh.sh

.PHONY: final-configured-preflight

final-configured-preflight:
	cd services/backend && uv run python -m myth_forge_api.cli final-configured-preflight --repo-root ../.. --output .local/final-configured-preflight.json

.PHONY: final-configured-evidence-plan

final-configured-evidence-plan:
	cd services/backend && uv run python -m myth_forge_api.cli final-configured-evidence-plan --repo-root ../.. --output .local/final-configured-evidence-plan.json

.PHONY: configured-live-evidence-bundle

configured-live-evidence-bundle:
	cd services/backend && uv run python -m myth_forge_api.cli configured-live-evidence-bundle --repo-root ../.. --output .local/configured-live-evidence-bundle.json

.PHONY: final-handoff-index

final-handoff-index:
	cd services/backend && uv run python -m myth_forge_api.cli final-handoff-index --repo-root ../.. --output .local/final-handoff-index.json

.PHONY: final-showcase-readiness

final-showcase-readiness:
	cd services/backend && uv run python -m myth_forge_api.cli final-showcase-readiness --repo-root ../.. --output .local/final-showcase-readiness.json

.PHONY: print-fulfillment-readiness

print-fulfillment-readiness:
	cd services/backend && uv run python -m myth_forge_api.cli print-fulfillment-readiness --repo-root ../.. --output .local/print-fulfillment-readiness.json

.PHONY: live-provider-evidence

live-provider-evidence:
	cd services/backend && uv run python -m myth_forge_api.cli live-provider-evidence --repo-root ../.. --output .local/live-provider-evidence.json

.PHONY: ios-device-launch-certificate

ios-device-launch-certificate:
	cd services/backend && uv run python -m myth_forge_api.cli ios-device-launch-certificate --repo-root ../.. --output .local/ios-device-launch-certificate.json

.PHONY: ios-device-launch-rehearsal

ios-device-launch-rehearsal:
	@services/backend/scripts/write_ios_device_launch_rehearsal.sh

.PHONY: final-acceptance-local final-acceptance-configured final-demo-launch final-demo-launch-local final-rehearsal-local

final-acceptance-local:
	@services/backend/scripts/write_final_acceptance_local.sh

final-acceptance-configured:
	@services/backend/scripts/write_final_acceptance_configured.sh

final-demo-launch: final-demo-launch-local

final-demo-launch-local:
	cd services/backend && uv run python -m myth_forge_api.cli final-demo-launch --mode local --repo-root ../.. --output .local/final-demo-launch-local.json

.PHONY: ios-deploy-runbook ios-deploy-runbook-local

ios-deploy-runbook:
	cd services/backend && uv run python -m myth_forge_api.cli ios-deploy-runbook --mode local --repo-root ../.. --output .local/ios-deploy-runbook-local.json

ios-deploy-runbook-local:
	@services/backend/scripts/write_ios_deploy_runbook_local.sh

.PHONY: ios-device-evidence-bundle

ios-device-evidence-bundle:
	cd services/backend && uv run python -m myth_forge_api.cli ios-device-evidence-bundle --repo-root ../.. --output .local/ios-device-evidence-bundle.json

final-rehearsal-local: backend-evaluate-local visual-regression-local final-acceptance-local final-demo-launch-local ios-deploy-runbook-local final-local-report-refresh-local

.PHONY: mobile-xcode-build

mobile-xcode-build:
	apps/mobile/ios/scripts/xcode_build_gate.sh

.PHONY: mobile-xcode-build-evidence

mobile-xcode-build-evidence:
	cd services/backend && uv run python -m myth_forge_api.cli mobile-xcode-build-evidence --repo-root ../.. --output .local/mobile-xcode-build-evidence.json

.PHONY: mobile-deploy-preflight

mobile-deploy-preflight:
	apps/mobile/ios/scripts/deploy_preflight.sh

.PHONY: mobile-deploy-preflight-evidence

mobile-deploy-preflight-evidence:
	cd services/backend && uv run python -m myth_forge_api.cli mobile-deploy-preflight-evidence --repo-root ../.. --output .local/mobile-deploy-preflight-evidence.json

.PHONY: mobile-write-deploy-config mobile-write-deploy-config-auto

mobile-write-deploy-config:
	apps/mobile/ios/scripts/write_deploy_local_config.sh

mobile-write-deploy-config-auto:
	PMF_BACKEND_BASE_URL=auto apps/mobile/ios/scripts/write_deploy_local_config.sh
