# AX1800M Mini Ultra 1-B — independent October Type-111 relay v0.5

**Current source version: v0.5 · code and offline tests only · NOT an OTA image or validated device release.**

This directory is the public source workspace for the pinned October `sdDongle` ABI. It contains no patched vendor executable, stock rollback TAR, uploader or phone logs. Earlier board-specific firmware downloads have been retired from the public release index. A separate [v0.5 RC2 test package](https://github.com/harman-f/harman-ax1800m-adapter-checker/releases/tag/ax1800m-miniultra-v0.5-rc2) contains proprietary vendor inputs outside this source directory.

## Implemented features in source

| Area | Current v0.5 source behavior | Evidence |
| --- | --- | --- |
| Independent cockpit video | Negotiates and relays Type 111 alongside stock Type 110; independent relay lifecycle, AES/ChaCha translation, selective teardown | Earlier v0.4 owner-reported car test; v0.5 offline tests only |
| HU display profile | Reads and validates single 111 display UUID/dimensions. Honors recognized `displays[].initialURL` when supplied; historical `/map` URL only as fallback | Host tests, not car-confirmed for v0.5 |
| Map/ETA commands | Recognizes `showUI`, `stopUI`, `updateViewArea`, `forceKeyFrame` with matching HU UUID, preserving full `params` | Host mocks; dongle ingress not measured with v0.5 |
| HU→phone command gap | Hooks the actual HU-event plist decoder, observes the stock phone sender, waits 150 ms before attempting **one** fallback only if stock did not submit that command | Static ABI audit, host tests; iOS acceptance unknown |
| New phone session | Coalesces two car-owned command slots (UI and ViewArea), retains nested params, guards against superseded values, replays after phone 111 setup | Host tests; reconnect behavior not field-qualified |
| Receive / teardown safety | Handles partial frames through timeouts, distinguishes auxiliary/native/full teardown, stale worker generations | Host tests; spontaneous keepalive/reconnect still open |
| Telemetry | Emits command type and recognized map setting enums; does not print raw URLs, display UUID, IP, arbitrary plist or phone identity | Source review/host tests |

**Do not infer that a car menu setting is repaired simply because the dongle submits a command.** A synchronous `submit_rc=0` is not an iPhone completion or visible cockpit change. The independent v0.5 source is an implementation candidate pending a controlled vehicle check.

## Source layout

```text
src/relay.c                   Stock ABI hooks, Type-111 worker, control bridge
src/hu_presentation_diag.h    Allowlisted map-URL parser (privacy-safe diagnostics)
src/vendor_abi.h              Pinned October vendor addresses, CF and AirPlay calls
src/initial_profile.h         Historic initial /map fallback and video-IDR helper
src/geometry.h                Dynamic video canvas values
tests/relay_test.c            Mocked lifecycle/control cases
tests/hu_presentation_diag_test.c   URL grammar and rejection cases
tests/geometry_test.c         Four canvas cases
build.py                      Zig MIPS shared-library + POSIX host tests only
SOURCE-MANIFEST.sha256        Integrity of published sources, docs and photos
assets/                       Owner-permitted photographs; not MIT-licensed
```

Detailed engineering notes and a [feature-by-feature comparison with October stock](../../docs/ax1800m/STOCK-VS-V05.md) are in [../../docs/ax1800m](../../docs/ax1800m/README.md).

## Exact target and observations

An owner-supplied Mini Ultra 1-B was observed with `platform=AX1800M`, `custom=suding`, product `v851se-yunlian-cp`, system `202603120956CA`, and after the October OTA protocol `20261008165747`. Vendor catalog entry: `ax_202610081657`. The identified October stock OTA TAR is 1,812,992 bytes (SHA-256 `13ca438ad4db00bbac0fa4650419df110bf17611a69525409261318a8bbade86`); pinned stock `sdDongle` SHA-256 `edff2ce4ae238d682fdc45be680d4cab919fc1be09bf398aaff4897289390bcb`. **Neither stock TAR nor vendor binary is redistributed here.**

An earlier owner-reported Skoda MHI2 `MHI2_ER_SKG13_P4526_MU1440` test observed CarPlay video/config, navigation symbols and zoom, including a reported 6,827-frame v0.4 session. This does not qualify the new v0.5 control bridge or make other head units/boards compatible. See [compatibility](../../docs/ax1800m/COMPATIBILITY-AND-RECOVERY.md).

## Reproduce the offline checks

Prerequisites: Python 3, Zig **0.14.1**, a POSIX C compiler and pthreads. On Linux/macOS/WSL:

```sh
ZIG=/path/to/zig-0.14.1 HOST_CC=cc python3 build.py
sha256sum -c SOURCE-MANIFEST.sha256
```

The script builds `build/libSdHOct.so` for MIPS32r2 and executes three **host** tests. The library is a source build product, **not** an OTA package and not directly flashable. CI verifies the pinned Zig download and ELF architecture; source cross-compilation cannot establish runtime ABI interoperability.

Validation is separated by feature in [TEST-MATRIX.md](../../docs/ax1800m/TEST-MATRIX.md). See [KNOWN-ISSUES.md](../../docs/ax1800m/KNOWN-ISSUES.md) before attempting any field work.

## License and publication scope

The source and project-authored code retain the [MIT license](LICENSE) and [third-party notices](THIRD_PARTY_NOTICES.md), including source lineage from [OMKE/wireless-carplay-virtual-cockpit](https://github.com/OMKE/wireless-carplay-virtual-cockpit) at commit `321191526ef26f98df87d85cd35d7597e5940ff1`. These patches were informed by disassembly of the proprietary, separately obtained October vendor binary; they are not presented as clean-room work. The original proprietary vendor binaries are **not included in this source directory or relicensed**. The separate experimental RC2 application ZIP includes manufacturer binaries under their existing proprietary status; raw logs/private test data are not distributed.

The two user-supplied photos below were published with the owner's permission only, are **not** covered by MIT, and cannot be freely redistributed or relicensed:

![Owner-authorized package photo](assets/miniultra1-b-packaging-photo.jpg)

![Owner-authorized package and adapter photo](assets/miniultra1-b-package-and-dongle-original.jpg)

The photos show exterior packaging/device appearance, not a verified PCB or SoC revision. For product context see [Carlinkit Mini Ultra1](https://www.carlinkit.com/ultra1); product names may span different hardware variants.
