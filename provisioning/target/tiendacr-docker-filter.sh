#!/usr/bin/env bash
set -euo pipefail

IPT=/usr/sbin/iptables
chain=DOCKER-USER
lab_iface="$(ip route show 10.10.10.0/24 | awk 'NR == 1 {for (i = 1; i <= NF; i++) if ($i == "dev") {print $(i + 1); exit}}')"
[ -n "$lab_iface" ]

# Preserve established sessions, permit the authorized lab source to Juice Shop,
# and reject all other sources for that published service.
if ! "$IPT" -w -C "$chain" -i "$lab_iface" -m conntrack \
  --ctstate ESTABLISHED,RELATED -j RETURN 2>/dev/null; then
  "$IPT" -w -I "$chain" 1 -i "$lab_iface" -m conntrack \
    --ctstate ESTABLISHED,RELATED -j RETURN
fi

if ! "$IPT" -w -C "$chain" -i "$lab_iface" -p tcp -s 10.10.10.30 \
  -m conntrack --ctorigdst 10.10.10.10 --ctorigdstport 3000 -j RETURN 2>/dev/null; then
  "$IPT" -w -I "$chain" 2 -i "$lab_iface" -p tcp -s 10.10.10.30 \
    -m conntrack --ctorigdst 10.10.10.10 --ctorigdstport 3000 -j RETURN
fi

if ! "$IPT" -w -C "$chain" -i "$lab_iface" -p tcp \
  -m conntrack --ctorigdst 10.10.10.10 --ctorigdstport 3000 -j DROP 2>/dev/null; then
  "$IPT" -w -I "$chain" 3 -i "$lab_iface" -p tcp \
    -m conntrack --ctorigdst 10.10.10.10 --ctorigdstport 3000 -j DROP
fi
