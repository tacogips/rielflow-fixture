# Vendor Egress Allowlist Sandbox

This fixture image is for rielflow package pre-install sandbox experiments.
It allows outbound HTTP/HTTPS only to AI vendor API hosts when the container is
run with `NET_ADMIN` so the entrypoint can install egress firewall rules.

Allowed host families:

- `api.openai.com` and `*.api.openai.com`
- `api.anthropic.com`
- `api2.cursor.sh`, `api.cursor.com`, `*.cursor.sh`, `*.cursorapi.com`

Build:

```bash
docker build -t rielflow-fixture/vendor-egress-allowlist:latest sandbox/vendor-egress-allowlist
```

Run against a package:

```bash
docker run --rm \
  --cap-add NET_ADMIN \
  --security-opt no-new-privileges \
  -v "$PWD/packages/fixture-clean-workflow:/package:ro" \
  rielflow-fixture/vendor-egress-allowlist:latest
```

For environments where Docker cannot grant `NET_ADMIN`, the static URL checker
can be tested without firewall installation:

```bash
docker run --rm \
  -e RIELFLOW_SANDBOX_FIREWALL=0 \
  -v "$PWD/packages/fixture-clean-workflow:/package:ro" \
  rielflow-fixture/vendor-egress-allowlist:latest
```

The firewall is IP based after startup DNS resolution. It is a sandbox fixture,
not a complete production egress gateway. Production use should pair it with
host/container runtime network policy and image pinning.
