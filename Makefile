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

.PHONY: backend-evaluate-3d backend-evaluate-npc backend-evaluate-local backend-evaluate-3d-configured backend-evaluate-npc-configured backend-evaluate-configured

backend-evaluate-3d:
	cd services/backend && uv run python -m myth_forge_api.cli evaluate-3d --provider local --suite default-v0 --output .local/3d-evaluation-local.json

backend-evaluate-npc:
	cd services/backend && uv run python -m myth_forge_api.cli evaluate-npc --provider local --suite default-v0 --tick-steps 2 --output .local/npc-evaluation-local.json

backend-evaluate-local: backend-evaluate-3d backend-evaluate-npc

backend-evaluate-3d-configured:
	cd services/backend && uv run python -m myth_forge_api.cli evaluate-3d --provider meshy --suite default-v0 --output .local/3d-evaluation-configured.json

backend-evaluate-npc-configured:
	cd services/backend && uv run python -m myth_forge_api.cli evaluate-npc --provider openai --suite default-v0 --tick-steps 2 --output .local/npc-evaluation-configured.json

backend-evaluate-configured: backend-evaluate-3d-configured backend-evaluate-npc-configured

.PHONY: backend-write-provider-env

backend-write-provider-env:
	@services/backend/scripts/write_backend_env.sh

.PHONY: provider-handoff

provider-handoff:
	@services/backend/scripts/write_provider_handoff.sh

.PHONY: resource-handoff

resource-handoff:
	@services/backend/scripts/write_resource_handoff.sh

.PHONY: final-apply-resources

final-apply-resources:
	@services/backend/scripts/apply_final_resources.sh

.PHONY: final-resource-init

final-resource-init:
	cd services/backend && sh scripts/init_final_resources.sh

.PHONY: final-resources-preflight

final-resources-preflight:
	@services/backend/scripts/write_final_resources_preflight.sh

.PHONY: final-resource-requirements

final-resource-requirements:
	@services/backend/scripts/write_final_resource_requirements.sh

.PHONY: final-resource-apply-preview

final-resource-apply-preview:
	@services/backend/scripts/write_final_resource_apply_preview.sh

.PHONY: final-resource-repair-preview final-resource-repair

final-resource-repair-preview:
	cd services/backend && uv run python -m myth_forge_api.cli final-resource-repair-preview --repo-root ../.. --output .local/final-resource-repair-preview.json

final-resource-repair:
	cd services/backend && uv run python -m myth_forge_api.cli final-resource-repair --repo-root ../.. --output .local/final-resource-repair.json

.PHONY: final-resource-fill-guide

final-resource-fill-guide:
	@services/backend/scripts/write_final_resource_fill_guide.sh

.PHONY: final-external-action-ledger

final-external-action-ledger:
	@services/backend/scripts/write_final_external_action_ledger.sh

.PHONY: final-launch-closure-packet

final-launch-closure-packet:
	@services/backend/scripts/write_final_launch_closure_packet.sh

.PHONY: local-showcase-smoke

local-showcase-smoke:
	cd services/backend && uv run python -m myth_forge_api.cli local-showcase-smoke --output .local/local-showcase-smoke.json

.PHONY: final-local-report-refresh final-local-report-refresh-local

final-local-report-refresh:
	@services/backend/scripts/write_final_local_report_refresh.sh

final-local-report-refresh-local:
	@services/backend/scripts/write_final_local_report_refresh.sh

.PHONY: final-configured-preflight

final-configured-preflight:
	@services/backend/scripts/write_final_configured_preflight.sh

.PHONY: final-configured-evidence-plan

final-configured-evidence-plan:
	@services/backend/scripts/write_final_configured_evidence_plan.sh

.PHONY: configured-live-evidence-bundle

configured-live-evidence-bundle:
	@services/backend/scripts/write_configured_live_evidence_bundle.sh

.PHONY: final-handoff-index

final-handoff-index:
	@services/backend/scripts/write_final_handoff_index.sh

.PHONY: final-showcase-readiness

final-showcase-readiness:
	@services/backend/scripts/write_final_showcase_readiness.sh

.PHONY: print-fulfillment-readiness

print-fulfillment-readiness:
	@services/backend/scripts/write_print_fulfillment_readiness.sh

.PHONY: live-provider-evidence

live-provider-evidence:
	@services/backend/scripts/write_live_provider_evidence.sh

.PHONY: ios-device-launch-certificate

ios-device-launch-certificate:
	@services/backend/scripts/write_ios_device_launch_certificate.sh

.PHONY: ios-device-launch-rehearsal

ios-device-launch-rehearsal:
	@services/backend/scripts/write_ios_device_launch_rehearsal.sh

.PHONY: ios-device-launch-rehearsal-readiness

ios-device-launch-rehearsal-readiness:
	@services/backend/scripts/write_ios_device_launch_rehearsal_readiness.sh

.PHONY: final-acceptance-local final-acceptance-configured final-demo-launch final-demo-launch-local final-demo-launch-configured final-rehearsal-local

final-acceptance-local:
	@services/backend/scripts/write_final_acceptance_local.sh

final-acceptance-configured:
	@services/backend/scripts/write_final_acceptance_configured.sh

final-demo-launch: final-demo-launch-local

final-demo-launch-local:
	cd services/backend && uv run python -m myth_forge_api.cli final-demo-launch --mode local --repo-root ../.. --output .local/final-demo-launch-local.json

final-demo-launch-configured:
	cd services/backend && uv run python -m myth_forge_api.cli final-demo-launch --mode configured --repo-root ../.. --output .local/final-demo-launch-configured.json

.PHONY: ios-deploy-runbook ios-deploy-runbook-local

ios-deploy-runbook:
	cd services/backend && uv run python -m myth_forge_api.cli ios-deploy-runbook --mode local --repo-root ../.. --output .local/ios-deploy-runbook-local.json

ios-deploy-runbook-local:
	@services/backend/scripts/write_ios_deploy_runbook_local.sh

.PHONY: ios-device-evidence-bundle

ios-device-evidence-bundle:
	@services/backend/scripts/write_ios_device_evidence_bundle.sh

final-rehearsal-local: backend-evaluate-local visual-regression-local final-acceptance-local final-demo-launch-local ios-deploy-runbook-local final-local-report-refresh-local

.PHONY: mobile-xcode-build

mobile-xcode-build:
	apps/mobile/ios/scripts/xcode_build_gate.sh

.PHONY: mobile-xcode-build-evidence

mobile-xcode-build-evidence:
	@services/backend/scripts/write_mobile_xcode_build_evidence.sh

.PHONY: mobile-deploy-preflight

mobile-deploy-preflight:
	apps/mobile/ios/scripts/deploy_preflight.sh

.PHONY: mobile-deploy-preflight-evidence

mobile-deploy-preflight-evidence:
	@services/backend/scripts/write_mobile_deploy_preflight_evidence.sh

.PHONY: mobile-write-deploy-config mobile-write-deploy-config-auto

mobile-write-deploy-config:
	apps/mobile/ios/scripts/write_deploy_local_config.sh

mobile-write-deploy-config-auto:
	PMF_BACKEND_BASE_URL=auto apps/mobile/ios/scripts/write_deploy_local_config.sh
