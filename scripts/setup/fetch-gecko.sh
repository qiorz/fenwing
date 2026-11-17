#!/bin/bash
# fetch-gecko.sh — 在 WSL(Ubuntu) 里以 dev 用户运行，取 pinned revision 源码
# 目标：/home/dev/ff/gecko （ext4，构建快）
set -x
PIN=5836a062726f715fda621338a17b51aff30d0a8c
mkdir -p /home/dev/ff
cd /home/dev/ff
if [ ! -d gecko/.git ]; then
  mkdir -p gecko
  cd gecko
  git init
  git remote add origin https://gitee.com/mirrors/gecko-dev.git
else
  cd gecko
fi
git fetch --depth 1 origin "$PIN"
rc=$?
if [ $rc -ne 0 ]; then
  echo "GITEE_FETCH_FAILED rc=$rc, fallback to github mirror"
  git remote set-url origin https://github.com/mozilla/gecko-dev.git
  git fetch --depth 1 origin "$PIN"
  rc=$?
fi
if [ $rc -ne 0 ]; then
  echo "FETCH_FAILED_ALL rc=$rc"
  exit 1
fi
git checkout --detach FETCH_HEAD
echo "HEAD=$(git rev-parse HEAD)"
echo "version=$(cat browser/config/version.txt 2>/dev/null)"
echo "log=$(git log -1 --format='%an %ad')"
echo "FILES=$(git ls-tree -r --name-only HEAD | wc -l)"
echo "GECKO_FETCH_DONE"
