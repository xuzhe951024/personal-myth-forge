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

.PHONY: backend-write-provider-env

backend-write-provider-env:
	@services/backend/scripts/write_backend_env.sh

.PHONY: mobile-xcode-build

mobile-xcode-build:
	apps/mobile/ios/scripts/xcode_build_gate.sh

.PHONY: mobile-deploy-preflight

mobile-deploy-preflight:
	apps/mobile/ios/scripts/deploy_preflight.sh

.PHONY: mobile-write-deploy-config

mobile-write-deploy-config:
	apps/mobile/ios/scripts/write_deploy_local_config.sh
