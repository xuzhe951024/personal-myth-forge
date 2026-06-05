# Mobile App Placeholder

The v0.1 client should be built as an iOS-first Unity project.

## Responsibilities

- Capture or upload real-world object imagery.
- Send an object observation and personal context capsule to the backend.
- Render the generated myth artifact in a small village scene.
- Present NPC reactions as text, animation state, movement, and world changes.
- Show the print candidate review screen before any fulfillment action.

## Backend Contract

The first client integration can still call the direct metadata endpoint for local
smoke tests:

```http
POST /v1/myth-sessions
```

with:

```json
{
  "object_observation": {
    "label": "old brass key",
    "materials": ["metal"],
    "source": "phone_capture"
  },
  "context_capsule": {
    "current_theme": "deadline pressure",
    "desired_tone": "tender, strange"
  }
}
```

The backend returns a complete myth session with NPC reactions, generated asset metadata, and a print candidate.

The P0.6 mobile capture path uses a two-call flow:

1. Upload object media and metadata with `POST /v1/object-captures`.
2. Create a session with `POST /v1/myth-sessions/from-capture`.

See `apps/mobile/contracts/capture-api.md` for the API contract and
`apps/mobile/fixtures/` for request payload examples. Local development stores
capture media under the backend `CAPTURE_STORAGE_DIR` setting and returns only
manifest URIs, never raw bytes.

## Unity Setup Notes

Create the Unity project in this directory when Unity is available locally. Use AR Foundation for future AR/camera paths, but v0.1 can start with camera upload plus a regular 3D scene.
