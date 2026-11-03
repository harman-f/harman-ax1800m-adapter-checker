# Wireless CarPlay adapter research, checker and firmware releases

**EXPERIMENTAL. Incorrect OTA firmware can disable an adapter.** Check [compatibility and recovery limitations](docs/ax1800m/COMPATIBILITY-AND-RECOVERY.md) before using a firmware release. Source-only code and firmware packages are different deliverables.

## Downloads

| Version | Purpose | Status |
| --- | --- | --- |
| [AX1800M Mini Ultra1-B **v0.5 RC2**](https://github.com/harman-f/harman-ax1800m-adapter-checker/releases/tag/ax1800m-miniultra-v0.5-rc2) | Application TAR, October stock app rollback, guarded uploader, source, checksums | **Current test candidate; offline PASS, NOT vehicle-tested** |
| [AX1800M v0.5 RC1](https://github.com/harman-f/harman-ax1800m-adapter-checker/releases/tag/ax1800m-miniultra-v0.5-rc1) | Early control-hook experiment | **SUPERSEDED — DO NOT INSTALL** |
| [AX1800M / Leon MU1447 October v0.2](https://github.com/harman-f/harman-ax1800m-adapter-checker/releases/tag/ax1800m-leon-mu1447-v0.2-legacy) | Older AX1800M system `202504180933CA` | Archived, **not** the new Mini Ultra system |
| [HW301 / CXZ521 / SEAT MU1409 v0.1](https://github.com/harman-f/harman-ax1800m-adapter-checker/releases/tag/hw301-seat-mu1409-v0.1-legacy) | Completely different HW301 hardware | Archived; **not interchangeable** |
| [AX1800M read-only checker **v0.2**](https://github.com/harman-f/harman-ax1800m-adapter-checker/releases/tag/ax1800m-readonly-checker-v0.2) | Read-only pre-/post-October identification, network probe, separate RC2 assessment | **No install authorization; not firmware** |

All downloadable ZIPs live in GitHub Releases, **not in the repository root**. The original two legacy firmware ZIPs and checker ZIP were migrated without changing their bytes. See the [release index and exact SHA-256 hashes](docs/ax1800m/RELEASES.md) and [firmware history](ADAPTER-FIRMWARE.md).

## AX1800M v0.5 engineering focus

The same MHI2/MU1440 Apple Maps ETA, map-surface and maneuver settings apply correctly over direct USB, but apparently not through the AX1800M wireless dongle. Working Type-111 **video** does not establish working HU→phone **control** forwarding.

The [current public v0.5 source](experimental/ax1800m-mini-ultra-october-relay/README.md) intercepts the actual HU binary-plist decoder, not the ineffective `eventMsgProc` GOT hypothesis in RC1. It retains HU-owned `showUI/stopUI` and `updateViewArea` commands, observes the stock phone sender, and implements a bounded 150-ms fallback/replay. The separate RC2 application package was built from this corrected source and tested **offline only**. There is **no recorded iPhone UI completion or vehicle acceptance for v0.5**.

Read [control-plane design](docs/ax1800m/CONTROL-PLANE.md), [test matrix](docs/ax1800m/TEST-MATRIX.md), [known issues](docs/ax1800m/KNOWN-ISSUES.md) and [compatibility/recovery](docs/ax1800m/COMPATIBILITY-AND-RECOVERY.md).

## Identity and recovery boundary

The owner-observed Mini Ultra 1-B sample reports `AX1800M/suding/v851se-yunlian-cp`, system `202603120956CA`, and after the October OTA protocol `20261008165747`. Exact stock catalog `ax_202610081657`, executable SHA-256 `edff2ce4ae238d682fdc45be680d4cab919fc1be09bf398aaff4897289390bcb`. Retail product names do not establish PCB/boot-ROM equivalence. An application rollback only works if the updater remains reachable; no complete hard-brick recovery is proven.

The [read-only checker v0.2 instructions](PROBE-README.md) cover the studied pre-/post-October identities but do not authorize firmware installation. Third-party vendor binaries in release archives are proprietary inputs; the source MIT license does not relicense them. Owner-authorized photographs in the source tree are not MIT-licensed.
