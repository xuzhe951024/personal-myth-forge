# Mobile App

The v0.1 client is iOS-first. P0.7 adds a native SwiftPM mobile core scaffold
under `apps/mobile/ios` so the capture-to-myth API loop can be tested locally
without changing global Xcode settings. Unity remains a later candidate for the
full 3D village scene once Unity is available locally.

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

## P0.7 iOS Scaffold

Run the local Swift contract tests with:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
```

The current machine's `xcodebuild` points at Command Line Tools, so simulator or
device builds are intentionally deferred. Do not run `xcode-select` or switch the
global developer directory as part of the local test path.

The SwiftUI files under `apps/mobile/ios/App` started as source scaffolding in
P0.7 and are now referenced by the P0.8 Xcode app shell. API keys and provider
secrets must not be committed into the mobile app; use backend-side provider
configuration instead.

## P0.8 Xcode App Shell

P0.8 adds:

```text
apps/mobile/ios/PersonalMythForge.xcodeproj
apps/mobile/ios/App/Info.plist
apps/mobile/ios/App/AppConfiguration.swift
```

Open `PersonalMythForge.xcodeproj` in full Xcode to continue simulator or device
deployment work. The current local environment only has Command Line Tools
selected, so do not run `xcode-select` as part of the repository verification
path.

Run the project-shell inspector with:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileProjectChecks
```

Then run the mobile core contract tests:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
```

`PMFBackendBaseURL` in `App/Info.plist` exposes the backend URL for the first API
client wiring. Provider API keys stay on the backend; the mobile app should
never commit OpenAI, Meshy, or print provider secrets.

## P0.9 Scan Capture Draft

P0.9 adds a SwiftPM-verifiable capture draft layer for:

- `single_photo`
- `photo_set`
- `manual_upload`
- `arkit_scan`

The draft layer converts mobile input state into `ObjectCaptureMetadata` plus
`[CaptureUpload]`, then the API client writes safe multipart filenames for image
and scan assets. Supported scan upload content types are:

- `model/gltf-binary` -> `scan_N.glb`
- `model/vnd.usdz+zip` -> `scan_N.usdz`
- `application/octet-stream` -> `scan_N.bin`

This iteration does not wire the live camera, PhotosPicker, or ARKit capture
runtime. It prepares the app source, validation rules, and backend upload
contract so a later full-Xcode/device iteration can attach real capture inputs.

Run:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileProjectChecks
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
```

Visual evidence lives at:

```text
docs/superpowers/verification/p0.9-ios-scan-capture.html
docs/superpowers/verification/assets/p0.9-ios-scan-capture-390x844.png
```
