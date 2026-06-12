from __future__ import annotations

CONFIGURED_FINAL_ACCEPTANCE_COMMAND = "make final-acceptance-configured"
CONFIGURED_FINAL_ACCEPTANCE_OUTPUT = (
    "services/backend/.local/final-acceptance-configured.json"
)
CONFIGURED_FINAL_ACCEPTANCE_COST_REVIEW_ACTION = (
    "approve live provider cost review before make final-acceptance-configured; "
    "--allow-live-provider-calls consent required"
)
