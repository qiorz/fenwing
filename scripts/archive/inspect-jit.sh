#!/bin/bash
set -u
cd /home/dev/ff/gecko
echo "=== arkweb-force-no-jit / AIRWEB flags in port ==="
grep -rn 'force-no-jit\|FORCE_NO_JIT\|force_no_jit\|NO_JIT' ports/ohos mobile/ohos widget/openharmony js/src 2>/dev/null | head -20
echo
echo "=== JIT prefs in geckoview prefs ==="
grep -rn 'javascript.options.jit\|wasm' mobile/ohos 2>/dev/null | head -10
echo
echo "=== our mozconfig ==="
cat /home/dev/ff/gecko/mozconfig 2>/dev/null || echo 'no mozconfig in tree'
