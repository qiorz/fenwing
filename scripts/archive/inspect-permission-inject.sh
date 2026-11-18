#!/bin/bash
set -u
cd /home/dev/ff/gecko
echo "=== objcopy / .permission injection in repo ==="
grep -rn '\.permission' --include=*.py --include=*.sh --include=*.md --include=*.cpp --include=*.gn --include=*.build --include=*.json ports/ohos docs 2>/dev/null | head -20
echo
echo "=== build scripts referencing permission.json ==="
grep -rn 'permission.json' --include=*.py --include=*.sh --include=*.md . 2>/dev/null | head -10
echo
echo "=== permission.json content ==="
cat ports/ohos/permission.json
echo
echo "=== any doc about 坚盾/ACL/JIT ==="
grep -rln '坚盾\|ALLOW_WRITABLE_CODE_MEMORY' --include=*.md --include=*.txt . 2>/dev/null | head -10
