.PHONY: backend-test backend-lint backend-dev

backend-test:
	cd services/backend && uv run pytest

backend-lint:
	cd services/backend && uv run ruff check .

backend-dev:
	cd services/backend && uv run uvicorn myth_forge_api.main:app --reload --port 8080

