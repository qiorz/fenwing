#!/usr/bin/env bash
#
# Build Gecko / SpiderMonkey for HarmonyOS aarch64.
#
# Contract (see scripts/README.md):
#   scripts/build_gecko.sh [--target js|gecko] [--jobs N] [--clean] [--print-config]
#
# - source tree : third_party/gecko/source   (never compiled by DevEco)
# - object dir  : build/gecko/obj-aarch64-ohos
# - log         : build/gecko/artifacts/<target>-build.log
#
# The script never invents artifacts. If the source tree or mach is missing it
# exits 2 with an actionable message; a failed build keeps the log for triage.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

TARGET="js"
JOBS=""
CLEAN=0
PRINT_CONFIG=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target)
      TARGET="${2:-}"
      shift 2
      ;;
    --jobs)
      JOBS="${2:-}"
      shift 2
      ;;
    --clean)
      CLEAN=1
      shift
      ;;
    --print-config)
      PRINT_CONFIG=1
      shift
      ;;
    -h|--help)
      sed -n '2,16p' "${BASH_SOURCE[0]}"
      exit 0
      ;;
    *)
      echo "ERROR: unknown argument: $1" >&2
      exit 64
      ;;
  esac
done

case "${TARGET}" in
  js|gecko) ;;
  *)
    echo "ERROR: --target must be 'js' or 'gecko' (got '${TARGET}')" >&2
    exit 64
    ;;
esac

SOURCE_DIR="${PROJECT_ROOT}/third_party/gecko/source"
OBJ_DIR="${PROJECT_ROOT}/build/gecko/obj-aarch64-ohos"
ARTIFACTS_DIR="${PROJECT_ROOT}/build/gecko/artifacts"
MOZCONFIG="${PROJECT_ROOT}/third_party/gecko/mozconfig/ohos-aarch64.mozconfig"
LOG_FILE="${ARTIFACTS_DIR}/${TARGET}-build.log"

# --- interpreter ------------------------------------------------------------
PYTHON="${PYTHON:-}"
if [[ -z "${PYTHON}" ]]; then
  if [[ -n "${DEVECO_SDK_HOME:-}" && -x "${DEVECO_SDK_HOME}/default/openharmony/native/llvm/python3/bin/python3" ]]; then
    PYTHON="${DEVECO_SDK_HOME}/default/openharmony/native/llvm/python3/bin/python3"
  elif command -v python3 >/dev/null 2>&1; then
    PYTHON="$(command -v python3)"
  fi
fi

if [[ -z "${PYTHON}" ]]; then
  echo "ERROR: no python3 interpreter found. Set PYTHON=/path/to/python3." >&2
  exit 2
fi

if [[ -z "${JOBS}" ]]; then
  JOBS="$("${PYTHON}" -c 'import os; print(os.cpu_count() or 4)')"
fi

# --- preflight --------------------------------------------------------------
if [[ "${PRINT_CONFIG}" -eq 1 ]]; then
  echo "PROJECT_ROOT=${PROJECT_ROOT}"
  echo "SOURCE_DIR=${SOURCE_DIR}"
  echo "OBJ_DIR=${OBJ_DIR}"
  echo "MOZCONFIG=${MOZCONFIG}"
  echo "LOG_FILE=${LOG_FILE}"
  echo "TARGET=${TARGET}"
  echo "JOBS=${JOBS}"
  echo "PYTHON=${PYTHON}"
  exit 0
fi

if [[ ! -d "${SOURCE_DIR}" ]]; then
  echo "ERROR: Gecko source tree not found at ${SOURCE_DIR}" >&2
  echo "       Run scripts/fetch_gecko.py first (see spec/gecko-porting-program/m1-report.md)." >&2
  exit 2
fi

if [[ ! -f "${SOURCE_DIR}/mach" ]]; then
  echo "ERROR: ${SOURCE_DIR}/mach not found - the checkout looks empty or partial." >&2
  echo "       Run scripts/fetch_gecko.py first; do not create a fake source tree." >&2
  exit 2
fi

if [[ ! -f "${MOZCONFIG}" ]]; then
  echo "ERROR: mozconfig not found at ${MOZCONFIG}" >&2
  exit 2
fi

mkdir -p "${OBJ_DIR}" "${ARTIFACTS_DIR}"

# mach is a Python entry point. Execute it through the interpreter: standalone
# executable files in writable directories return EPERM on this device.
export MOZCONFIG
export MOZ_OBJDIR="${OBJ_DIR}"
export MOZ_NOSPAM=1
export MOZBUILD_STATE_PATH="${PROJECT_ROOT}/build/gecko/mozbuild-state"

echo "==> target=${TARGET} jobs=${JOBS}"
echo "==> objdir=${OBJ_DIR}"
echo "==> log=${LOG_FILE}"

if [[ "${CLEAN}" -eq 1 ]]; then
  echo "==> clobber"
  ( cd "${SOURCE_DIR}" && "${PYTHON}" mach clobber ) 2>&1 | tee "${LOG_FILE}"
fi

cd "${SOURCE_DIR}"
set +e
"${PYTHON}" mach build -j "${JOBS}" 2>&1 | tee -a "${LOG_FILE}"
STATUS=${PIPESTATUS[0]}
set -e

if [[ "${STATUS}" -ne 0 ]]; then
  echo "ERROR: mach build failed (exit ${STATUS}). Log: ${LOG_FILE}" >&2
  echo "       Record the blocking point in spec/gecko-porting-program/m1-report.md." >&2
  exit "${STATUS}"
fi

echo "==> build finished: ${LOG_FILE}"
echo "==> next: scripts/stage_gecko_artifacts.py --copy"
