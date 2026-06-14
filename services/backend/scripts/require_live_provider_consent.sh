#!/usr/bin/env sh
set -eu

if [ "${PMF_ALLOW_LIVE_PROVIDER_CALLS:-}" = "1" ]; then
  exit 0
fi

printf '%s\n' "Live provider calls are blocked." >&2
printf '%s\n' "Set PMF_ALLOW_LIVE_PROVIDER_CALLS=1 only after explicit Meshy/OpenAI cost consent." >&2
printf '%s\n' "No live provider command was run." >&2
exit 2
