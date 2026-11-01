# Runtime Dependencies

## Browser Runtime

- Three.js `0.167.0` from jsDelivr, including OrbitControls, WebXR helpers, and ConvexGeometry.
- `qrcode-generator` `1.4.4` from jsDelivr, loaded only when QR sharing is requested.
- Browser support target: current Chromium, Firefox, Safari, and WebGL-capable mobile browsers.

## Validation And Build

- Python 3.10+ for catalog validation, migration, manifest, deployment, and smoke scripts.
- Node 18+ for the procedural generator test.
- `jsonschema` `4.23.0` in CI for Draft 2020-12 validation.
- Chromium in CI for HTTP, file://, stable-link, catalog, system, transition, and mobile smoke tests.

## GitHub Actions

- `actions/checkout@v4`
- `actions/setup-python@v5`
- `actions/setup-node@v4`
- `actions/configure-pages@v5`
- `actions/upload-pages-artifact@v3`
- `actions/deploy-pages@v4`

## Update Policy

- Keep browser CDN versions explicit and update them deliberately with a smoke-test run.
- Keep CI Python dependencies pinned.
- Review GitHub Action tags regularly and migrate to commit-SHA pinning when the repository release policy is finalized.
- Do not add a framework or backend without a measured product need.
