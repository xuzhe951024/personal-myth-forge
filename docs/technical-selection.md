# Technical Selection

## Recommendation

Use a mobile-first client with a cloud backend:

```text
iOS Unity client
  -> FastAPI backend
  -> OpenAI-powered object understanding and myth direction
  -> Meshy-first 3D provider adapter
  -> Treatstock-first print quote adapter
  -> future MCP-compatible personal context skill
```

## Client

Start with Unity on iOS. The player-facing experience depends on phone-native capture, touch interaction, and a direct sense that a real object crosses into the game world. Android support should follow after the core loop is proven.

Unity owns:

- object capture and upload
- small village rendering
- generated GLB loading
- NPC movement, animation states, and interaction presentation
- print candidate review UI

## Backend

Use Python FastAPI for v0.1 because the backend is orchestration-heavy and will integrate AI, asset processing, print adapters, and future agent tools. Keep all provider integrations behind internal adapters.

Current scaffold:

- `myth_forge_api.domain.models` defines the session contract.
- `myth_forge_api.domain.pipeline` creates a deterministic local myth session.
- `myth_forge_api.providers.three_d` stands in for Meshy, Tripo, Rodin, or self-hosted 3D generation.
- `myth_forge_api.providers.printing` stands in for Treatstock, Sculpteo, or future fulfillment partners.

## AI NPC

Skip voice in v0.1. NPC autonomy should come from memory, belief, interpretation, plans, and world changes. NPCs should not be hard-coded to one fixed action list, but all generated plans still pass through world-state arbitration before Unity executes them.

## 3D Generation

Free-form 3D generation is part of the core product. v0.1 should not restrict output to fixed relic templates.

The system should separate:

- `game_asset`: free-form generated 3D artifact for the game world.
- `print_asset`: reviewed and repaired derivative for physical fulfillment.

Meshy is the first likely provider because it supports text/image to 3D, common game formats, STL/3MF, remesh, resize, and printability-related operations. Tripo and Rodin remain adapter-compatible candidates.

## Print Fulfillment

The first production path should quote and review before order placement. Treatstock is likely the first low-cost provider adapter. Sculpteo can be added as a higher-reliability industrial option.

## Personal Context Skill

The personal context skill should be MCP-compatible and return only user-approved context capsules. It must not return raw email, calendar, chat, document bodies, addresses, payment data, or direct personal identifiers.

