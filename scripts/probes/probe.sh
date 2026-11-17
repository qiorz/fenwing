#!/bin/bash
echo "=== date ==="; date
echo "=== dev user ==="; id dev 2>/dev/null || echo "no dev user yet"
echo "=== processes ==="
ps -eo pid,pcpu,etime,args --no-headers | grep -Ev '\[|grep ' | head -20
echo "=== tools ==="
for t in clang gcc cmake ninja python3 python3.11 rustc cargo; do
  p=$(command -v $t 2>/dev/null)
  echo "$t -> ${p:-MISS}"
done
echo "=== apt lists count ==="; ls /var/lib/apt/lists 2>/dev/null | wc -l
echo "=== disk ==="; df -h / | tail -1
echo "=== dns ==="
getent hosts static.rust-lang.org >/dev/null 2>&1 && echo dns-ok || echo dns-FAIL
echo "=== /tmp bootstrap ==="; ls -l /tmp/02-wsl-bootstrap.sh 2>/dev/null
echo "=== bootstrap log? ==="; ls -l /tmp/*.log 2>/dev/null
