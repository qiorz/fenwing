# Gecko for HarmonyOS - NAPI bridge
#
# Built by hvigor through gecko/build-profile.json5 -> externalNativeOptions.
# The HarmonyOS NDK toolchain supplies CMAKE_SYSROOT and -L for the target ABI,
# so system libraries are linked by their soname.
#
# Rules:
#  - Never add Gecko/SpiderMonkey *source* here. Sources live in third_party/gecko.
#  - Prebuilt .so files are staged into ../libs/${OHOS_ARCH} by
#    scripts/stage_gecko_artifacts.py and are linked from there.

cmake_minimum_required(VERSION 3.5.0)
project(gecko_napi)

set(NATIVERENDER_ROOT_PATH ${CMAKE_CURRENT_SOURCE_DIR})

if(NOT DEFINED OHOS_ARCH)
    set(OHOS_ARCH "arm64-v8a")
endif()

set(GECKO_LIBS_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../libs/${OHOS_ARCH}")

if(DEFINED PACKAGE_FIND_FILE)
    include(${PACKAGE_FIND_FILE})
endif()

include_directories(
    ${NATIVERENDER_ROOT_PATH}
    ${NATIVERENDER_ROOT_PATH}/include
)

set(GECKO_SOURCES
    src/gecko_module.cpp
)

# ---------------------------------------------------------------------------
# M1 SpiderMonkey adapter: compiled only when libmozjs.so + jsapi.h are staged.
# ---------------------------------------------------------------------------
set(MOZJS_INCLUDE_DIR "${GECKO_LIBS_DIR}/include")
set(MOZJS_LIB "${GECKO_LIBS_DIR}/libmozjs.so")
set(GECKO_HAVE_MOZJS OFF)
if(EXISTS "${MOZJS_INCLUDE_DIR}/jsapi.h" AND EXISTS "${MOZJS_LIB}")
    set(GECKO_HAVE_MOZJS ON)
    list(APPEND GECKO_SOURCES src/mozjs_eval.cpp)
    message(STATUS "gecko: libmozjs found - evaluateScript enabled")
else()
    message(STATUS "gecko: libmozjs not staged - evaluateScript returns UNSUPPORTED")
endif()

add_library(gecko_napi SHARED ${GECKO_SOURCES})

target_compile_features(gecko_napi PRIVATE cxx_std_17)
target_compile_options(gecko_napi PRIVATE
    -Wall
    -Wextra
    -fno-exceptions
    -fno-rtti
    -fvisibility=hidden
)

target_compile_definitions(gecko_napi PRIVATE
    GECKO_NAPI_LIB_NAME="libgecko_napi.so"
)

if(GECKO_HAVE_MOZJS)
    target_compile_definitions(gecko_napi PRIVATE GECKO_HAVE_MOZJS=1)
    target_include_directories(gecko_napi PRIVATE "${MOZJS_INCLUDE_DIR}")
    # SpiderMonkey 公开头文件依赖 js-confdefs.h 里的平台宏（XP_UNIX/XP_LINUX/OHOS）
    target_compile_options(gecko_napi PRIVATE -include js-confdefs.h)
endif()

target_link_libraries(gecko_napi PUBLIC
    libace_napi.z.so
    libhilog_ndk.z.so
)

if(GECKO_HAVE_MOZJS)
    target_link_libraries(gecko_napi PUBLIC "${MOZJS_LIB}")
endif()

# ---------------------------------------------------------------------------
# M0 Rust smoke bridge (optional): built by scripts/build_rust_smoke.sh.
# When absent the NAPI layer reports UNSUPPORTED instead of failing the build.
# ---------------------------------------------------------------------------
set(OHOS_SMOKE_LIB "${GECKO_LIBS_DIR}/libohos_smoke.so")
if(EXISTS "${OHOS_SMOKE_LIB}")
    target_compile_definitions(gecko_napi PRIVATE GECKO_HAVE_RUST_SMOKE=1)
    target_link_libraries(gecko_napi PUBLIC "${OHOS_SMOKE_LIB}")
    message(STATUS "gecko: linking Rust smoke bridge ${OHOS_SMOKE_LIB}")
else()
    message(WARNING "gecko: libohos_smoke.so not staged - rustAdd will return UNSUPPORTED")
endif()
