#!/usr/bin/env sh
set -eu

ALLOWLIST_FILE="${RIELFLOW_VENDOR_ALLOWLIST:-/opt/rielflow-sandbox/allowlist.txt}"

resolve_hosts() {
  awk '
    /^[[:space:]]*#/ { next }
    /^[[:space:]]*$/ { next }
    {
      gsub(/^[[:space:]]+|[[:space:]]+$/, "", $0)
      gsub(/^\*\./, "", $0)
      print $0
    }
  ' "$ALLOWLIST_FILE" | sort -u
}

install_firewall() {
  if ! command -v iptables >/dev/null 2>&1; then
    echo "rielflow sandbox: iptables is unavailable; refusing firewall mode" >&2
    return 1
  fi

  iptables -F OUTPUT
  iptables -P OUTPUT DROP
  iptables -A OUTPUT -o lo -j ACCEPT
  iptables -A OUTPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

  # DNS is needed only during startup to resolve the configured vendor hosts.
  iptables -A OUTPUT -p udp --dport 53 -j ACCEPT
  iptables -A OUTPUT -p tcp --dport 53 -j ACCEPT

  for host in $(resolve_hosts); do
    for ip in $(getent ahostsv4 "$host" | awk '{ print $1 }' | sort -u); do
      iptables -A OUTPUT -p tcp -d "$ip" --dport 443 -j ACCEPT
      iptables -A OUTPUT -p tcp -d "$ip" --dport 80 -j ACCEPT
    done
  done
}

if [ "${RIELFLOW_SANDBOX_FIREWALL:-1}" = "1" ]; then
  if ! install_firewall; then
    cat >&2 <<'MSG'
rielflow sandbox: failed to install firewall rules.
Run the container with NET_ADMIN, for example:
  docker run --rm --cap-add NET_ADMIN --security-opt no-new-privileges ...
MSG
    exit 126
  fi
else
  echo "rielflow sandbox: firewall disabled by RIELFLOW_SANDBOX_FIREWALL=0" >&2
fi

exec "$@"
