# Capture API Contract

P0.6 mobile clients use two calls:

1. `POST /v1/object-captures`
2. `POST /v1/myth-sessions/from-capture`

## Upload Object Capture

Request: `multipart/form-data`

- `metadata_json`: JSON matching `apps/mobile/fixtures/object-capture-metadata.json`
- `files`: one or more image or scan files

Example:

```bash
curl -X POST http://127.0.0.1:8080/v1/object-captures \
  -F 'metadata_json={"label":"old brass key","materials":["metal","brass"],"source":"phone_capture","capture_mode":"single_photo","visual_notes":"worn teeth"}' \
  -F 'files=@/path/to/key.jpg;type=image/jpeg'
```

The response is an `ObjectCapture` manifest. It contains `local-capture://` URIs in
local development and never returns raw file bytes.

## Create Myth From Capture

```bash
curl -X POST http://127.0.0.1:8080/v1/myth-sessions/from-capture \
  -H 'Content-Type: application/json' \
  -d @apps/mobile/fixtures/myth-session-from-capture.json
```

Unity should render `generated_asset.uri` when it is a remote GLB. Local stub URIs
are metadata-only and should use a placeholder artifact.
