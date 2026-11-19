#!/bin/bash
cd /home/dev/ff/gecko
sed -n '555,625p' dom/media/platforms/PDMFactory.cpp
echo "=== callers of Startup ==="
grep -rn '->Startup()' dom/media | grep -i pdm | head
