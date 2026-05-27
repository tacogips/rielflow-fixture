FROM debian:bookworm-slim

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    dnsutils \
    iproute2 \
    iptables \
    python3 \
  && rm -rf /var/lib/apt/lists/*

COPY allowlist.txt /opt/rielflow-sandbox/allowlist.txt
COPY bin/entrypoint.sh /usr/local/bin/rielflow-vendor-egress-entrypoint
COPY bin/sandbox-check.py /usr/local/bin/rielflow-sandbox-check

RUN chmod +x \
  /usr/local/bin/rielflow-vendor-egress-entrypoint \
  /usr/local/bin/rielflow-sandbox-check

ENV RIELFLOW_VENDOR_ALLOWLIST=/opt/rielflow-sandbox/allowlist.txt
ENTRYPOINT ["rielflow-vendor-egress-entrypoint"]
CMD ["rielflow-sandbox-check", "/package"]
