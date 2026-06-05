# Initial Design

## Product Thesis

The product is a mobile-first personalized myth simulator. A player captures a real object, supplies or authorizes a concise personal context capsule, and watches a small AI-driven world reinterpret that object as a divine artifact. The game then generates a 3D artifact for in-game use and a printable derivative for real-world fulfillment.

## v0.1 Scope

v0.1 focuses on a single-session vertical slice:

- iOS-first mobile experience, with desktop used for backend and editor debugging.
- No voice NPCs.
- High-autonomy NPC planning with world-state arbitration.
- Free-form 3D generation is required for the in-game artifact.
- Printable assets are derivatives of generated 3D artifacts, not fixed template categories.
- Third-party print service integration starts with quote/review, not fully automatic order placement.

## Core Loop

```text
mobile object capture
  -> object understanding
  -> personal context capsule
  -> myth director
  -> free-form 3D game artifact
  -> NPC autonomous interpretation
  -> printable derivative
  -> print quote and user approval
```

## Architectural Boundaries

- Mobile client owns capture, scene rendering, interaction, and artifact presentation.
- Backend owns AI orchestration, session state, generated asset metadata, NPC planning, and provider adapters.
- 3D providers are wrapped behind an internal adapter so Meshy, Tripo, Rodin, and future self-hosted models can be swapped.
- Print providers are wrapped behind an internal adapter so Treatstock, Sculpteo, and future fulfillment partners can be swapped.
- Personal context is accepted as summary capsules only; raw private documents are out of scope for v0.1.

## Safety Boundaries

Generated assets and print candidates must pass review before fulfillment. The system must reject or downgrade requests involving weapons, realistic human faces without consent, private identifying data, copyrighted characters, company secrets, or shapes that are likely to fail or harm users when printed.

