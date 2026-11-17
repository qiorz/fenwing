//! M0 smoke cdylib for Gecko for HarmonyOS.
//!
//! Goal: prove the full ArkTS -> NAPI -> Rust call path works when the library
//! is packaged inside the `gecko` HSP. Nothing here touches Gecko; this crate
//! exists so a failure in the chain is unambiguous.
//!
//! Exported ABI is deliberately C-only (`#[no_mangle] extern "C"`) and uses
//! fixed-width integers so the NAPI side can bind it without a header.

use core::ffi::c_int;

/// ABI version of this bridge. Bump when signatures change.
pub const BRIDGE_ABI_VERSION: u32 = 1;

/// Adds two 32-bit integers with saturation instead of panicking.
///
/// `panic = "abort"` is set for this crate: an overflow must never unwind
/// across the FFI boundary into the ArkTS runtime.
#[no_mangle]
pub extern "C" fn ohos_rust_add(left: c_int, right: c_int) -> c_int {
    left.saturating_add(right)
}

/// Returns the ABI version so the NAPI layer can detect a stale `.so`.
#[no_mangle]
pub extern "C" fn ohos_rust_bridge_version() -> u32 {
    BRIDGE_ABI_VERSION
}

/// Round-trip check used by the debug page: returns `input * 2 + 1`.
#[no_mangle]
pub extern "C" fn ohos_rust_probe(input: c_int) -> c_int {
    input.saturating_mul(2).saturating_add(1)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn add_is_saturating() {
        assert_eq!(ohos_rust_add(2, 40), 42);
        assert_eq!(ohos_rust_add(c_int::MAX, 1), c_int::MAX);
    }

    #[test]
    fn probe_shape() {
        assert_eq!(ohos_rust_probe(5), 11);
        assert_eq!(ohos_rust_bridge_version(), BRIDGE_ABI_VERSION);
    }
}
