# Personal Myth Skill Placeholder

This package will become the MCP-compatible skill surface for work and life agents.

## v0.1 Contract

The skill should expose context capsules, not raw private data.

Candidate tools:

- `create_context_capsule`
- `start_myth_session`
- `generate_relic_brief`
- `quote_print_candidate`

## Context Capsule Shape

```json
{
  "current_theme": "new beginning",
  "desired_tone": "hopeful but mysterious",
  "recent_milestone": "finished a difficult project draft"
}
```

## Privacy Rule

The skill must not return raw email bodies, calendar descriptions, chat logs, document text, direct contact details, addresses, or payment data. It returns only user-approved summaries.

