#!/bin/bash
echo "=== procs ==="
ps -eo pid,etime,args --no-headers | grep -E 'git|fetch-gecko' | grep -v grep | head -10
echo "=== gecko dir ==="
ls -la /home/dev/ff 2>/dev/null
du -sh /home/dev/ff/gecko 2>/dev/null || true
echo "=== fetch log ==="
cat /home/dev/ff/fetch.log 2>/dev/null | tail -20
