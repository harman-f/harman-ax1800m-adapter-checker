# AX1800M / Suding / Mini Ultra 1-B: engineering documentation

This is the canonical index for the **current v0.5 independent Type-111 source**, distinguished from the older download ZIPs and the strict read-only checker.

| Document | Read when… |
| --- | --- |
| [CONTROL-PLANE.md](CONTROL-PLANE.md) | Understanding USB vs wireless, dynamic `showUI` maps URL, HU ingress/phone sender, cache/fallback/replay |
| [TEST-MATRIX.md](TEST-MATRIX.md) | Checking what was actually exercised: previous car observation vs current host tests and MIPS build |
| [KNOWN-ISSUES.md](KNOWN-ISSUES.md) | Diagnosing keepalive after teardown, `port_valid=0`, UI delivery and asynchronous completion |
| [COMPATIBILITY-AND-RECOVERY.md](COMPATIBILITY-AND-RECOVERY.md) | Establishing exact firmware compatibility, checker version mismatch and rollback limitations |
| [CHANGELOG.md](CHANGELOG.md) | Mapping v0.2/v0.3/v0.4 to v0.5 fixes without confusing source-only and OTA releases |

Code: [experimental/ax1800m-mini-ultra-october-relay](../../experimental/ax1800m-mini-ultra-october-relay/README.md). Root [repository overview](../../README.md).

**Evidence levels:** `implemented` means source exists; `host PASS` means tests executed on non-target machines; `target observed` means a reported device/vehicle log or screen, not third-party certification; `unverified` must not be treated as working. No v0.5 firmware package or hardware acceptance exists here.
