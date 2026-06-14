#!/usr/bin/env sh
set -eu

if [ "${PMF_ALLOW_PRINT_PROVIDER_CALLS:-}" = "1" ]; then
  exit 0
fi

printf '%s\n' "Print provider calls are blocked." >&2
printf '%s\n' "Set PMF_ALLOW_PRINT_PROVIDER_CALLS=1 only after explicit Treatstock quote cost consent." >&2
printf '%s\n' "No print provider command was run." >&2
exit 2
