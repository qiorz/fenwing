#!/usr/bin/env bash
#
# Build the M0 Rust smoke cdylib for HarmonyOS aarch64 and copy it into the HSP.
#
#   scripts/build_rust_smoke.sh [--release]
#
# Outputs:
#   build/gecko/rust-target/aarch64-unknown-linux-ohos/<profile>/libohos_smoke.so
#   gecko/src/main/libs/arm64-v8a/libohos_smoke.so
#
# The linker is the SDK's aarch64-unknown-linux-ohos-clang so the OHOS sysroot
# and target flags are applied. No standalone binary is executed.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

PROFILE="debug"
for argument in "$@"; do
  case "${argument}" in
    --release) PROFILE="release" ;;
    --debug) PROFILE="debug" ;;
    -h|--help)
      sed -n '2,14p' "${BASH_SOURCE[0]}"
      exit 0
      ;;
    *)
      echo "ERROR: unknown argument: ${argument}" >&2
      exit 64
      ;;
  esac
done

CARGO="${CARGO:-${HOME}/.harmonybrew/bin/cargo}"
TARGET="aarch64-unknown-linux-ohos"
CRATE_DIR="${PROJECT_ROOT}/gecko/rust/ohos-smoke"
TARGET_DIR="${PROJECT_ROOT}/build/gecko/rust-target"
# Canonical staging location (plan.md layout) + hvigor packaging location.
# hvigor's ProcessLibs task only collects prebuilt libs from <module>/libs/<abi>,
# so the same file must exist in both places.
LIB_DIR="${PROJECT_ROOT}/gecko/src/main/libs/arm64-v8a"
PACK_LIB_DIR="${PROJECT_ROOT}/gecko/libs/arm64-v8a"
STAGED_LIB="${LIB_DIR}/libohos_smoke.so"

if [[ ! -x "${CARGO}" ]]; then
  echo "ERROR: cargo not found at ${CARGO}. Set CARGO=/path/to/cargo." >&2
  exit 2
fi

if [[ -z "${DEVECO_SDK_HOME:-}" ]]; then
  echo "ERROR: DEVECO_SDK_HOME is not set (needed for the OHOS linker)." >&2
  exit 2
fi

LINKER="${DEVECO_SDK_HOME}/default/openharmony/native/llvm/bin/${TARGET}-clang"
if [[ ! -x "${LINKER}" ]]; then
  echo "ERROR: OHOS clang not found at ${LINKER}" >&2
  exit 2
fi

export CARGO_TARGET_AARCH64_UNKNOWN_LINUX_OHOS_LINKER="${LINKER}"
export CARGO_TARGET_DIR="${TARGET_DIR}"
export CARGO_NET_OFFLINE="${CARGO_NET_OFFLINE:-false}"

echo "==> cargo build (${PROFILE}) target=${TARGET}"
if [[ "${PROFILE}" == "release" ]]; then
  "${CARGO}" build --manifest-path "${CRATE_DIR}/Cargo.toml" --target "${TARGET}" --release
else
  "${CARGO}" build --manifest-path "${CRATE_DIR}/Cargo.toml" --target "${TARGET}"
fi

BUILT_LIB="${TARGET_DIR}/${TARGET}/${PROFILE}/libohos_smoke.so"
if [[ ! -f "${BUILT_LIB}" ]]; then
  echo "ERROR: expected ${BUILT_LIB} was not produced." >&2
  exit 1
fi

mkdir -p "${LIB_DIR}" "${PACK_LIB_DIR}"
cp "${BUILT_LIB}" "${STAGED_LIB}"
cp "${BUILT_LIB}" "${PACK_LIB_DIR}/libohos_smoke.so"
echo "==> staged ${STAGED_LIB}"
echo "==> packaged ${PACK_LIB_DIR}/libohos_smoke.so"
echo "==> verify: $(dirname "${BASH_SOURCE[0]}")/verify_gecko_bundle.py"
