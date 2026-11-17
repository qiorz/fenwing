#!/bin/bash
set -u
cd /home/dev/ff/gecko/widget/openharmony
ls -la
echo
echo "=== child window / widget creation ==="
grep -rn 'eWindowType_child\|CreateChild\|childWindow\|SetParent' *.cpp *.h 2>/dev/null | head -20
echo
echo "=== nsWindow::Show / visibility ==="
grep -rn 'void nsWindow::Show\|nsWindow::Hide\|MakeFullScreen\|SetSize' *.cpp 2>/dev/null | head -20
echo
echo "=== surface / OHNativeWindow per window ==="
grep -rn 'OHNativeWindow\|NativeWindow' *.cpp *.h 2>/dev/null | head -30
echo
echo "=== browser element handling ==="
grep -rn 'browser' *.cpp *.h 2>/dev/null | head -20
