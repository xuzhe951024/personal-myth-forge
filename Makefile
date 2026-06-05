.PHONY: backend-test backend-lint backend-dev backend-demo backend-generate-local

backend-test:
	cd services/backend && uv run pytest

backend-lint:
	cd services/backend && uv run ruff check .

backend-dev:
	cd services/backend && uv run uvicorn myth_forge_api.main:app --reload --port 8080

backend-demo:
	cd services/backend && uv run uvicorn myth_forge_api.main:app --reload --port 8080

backend-generate-local:
	cd services/backend && uv run python -m myth_forge_api.cli generate-asset --provider local --prompt "Create a brass key relic worshiped by a tiny village."
