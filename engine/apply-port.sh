#!/usr/bin/env bash
# Check out mozilla-central at the pinned revision and apply the OHOS port patch.
#
# usage: ./apply-port.sh [dest-dir]      (default: ./gecko)
set -euo pipefail

REV=5836a062726f715fda621338a17b51aff30d0a8c
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PATCH="$HERE/patches/firefox-ohos-gecko-5836a06272.patch"
DEST=${1:-./gecko}

[ -f "$PATCH" ] || { echo "patch not found: $PATCH" >&2; exit 1; }
command -v git >/dev/null || { echo "git is required" >&2; exit 1; }

if [ -d "$DEST/.git" ]; then
  echo "[1/3] reusing existing repository: $DEST"
  git -C "$DEST" cat-file -e "${REV}^{commit}" 2>/dev/null || git -C "$DEST" fetch --depth 1 origin "$REV"
else
  echo "[1/3] cloning gecko-dev (blobless, no checkout): $DEST"
  git clone --filter=blob:none --no-checkout https://gitee.com/mirrors/gecko-dev.git "$DEST"
  git -C "$DEST" fetch --depth 1 origin "$REV"
fi

echo "[2/3] checking out $REV"
git -C "$DEST" checkout --detach "$REV"

echo "[3/3] applying the port patch (1128 files)"
git -C "$DEST" apply -p1 --whitespace=nowarn "$PATCH"

cat <<EOF

Done. Next:

  cp "$HERE/mozconfig" "$DEST/mozconfig"
  cd "$DEST"
  export OHOS_SDK_NATIVE=/opt/ohos-sdk/native
  ./mach build -j\$(nproc)

Artifacts land in obj-aarch64-unknown-linux-ohos/dist/bin/.
EOF
