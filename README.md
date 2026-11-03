# Wireless CarPlay adapter research, checker and firmware releases

**EXPERIMENTAL. Incorrect OTA firmware can disable an adapter.** Check [compatibility and recovery limitations](docs/ax1800m/COMPATIBILITY-AND-RECOVERY.md) before using a firmware release. Source-only code and firmware packages are different deliverables.

## Current downloads — only two maintained packages

| Package | What it is | Validation |
| --- | --- | --- |
| [AX1800M Mini Ultra 1-B **v0.5 RC2**](https://github.com/harman-f/harman-ax1800m-adapter-checker/releases/tag/ax1800m-miniultra-v0.5-rc2) | Experimental *application* TAR with guarded uploader and matching October application rollback | Offline tests PASS; **no device or vehicle acceptance** |
| [AX1800M read-only checker **v0.2**](https://github.com/harman-f/harman-ax1800m-adapter-checker/releases/tag/ax1800m-readonly-checker-v0.2) | GET-only identity/network diagnostic, no firmware flashing | Python 3.9/3.12 offline PASS; device execution pending |

Neither the checker nor model strings authorize installation. Download only from these current Release entries. Superseded and incompatible builds are not recommended or linked as downloads; historical Git tags remain provenance, not install instructions. See [release and checksum guidance](docs/ax1800m/RELEASES.md).

## Stock October application versus experimental v0.5 RC2

The source comparison is documented in [**Stock vs v0.5 feature matrix**](docs/ax1800m/STOCK-VS-V05.md). In short: the October stock application supplies the existing wireless CarPlay main-display path, while the custom relay adds a separate Type-111 cockpit video path, HU presentation-command observation and bounded fallback/replay. v0.5 **does not** repair or replace the stock Wi-Fi/Bluetooth transport, keepalive or `port_valid=0` reconnect path. The newly added command bridge has **not** been validated on a phone or in the car.
## AX1800M v0.5 engineering focus

The same MHI2/MU1440 Apple Maps ETA, map-surface and maneuver settings apply correctly over direct USB, but apparently not through the AX1800M wireless dongle. Working Type-111 **video** does not establish working HU→phone **control** forwarding.

The [current public v0.5 source](experimental/ax1800m-mini-ultra-october-relay/README.md) intercepts the actual HU binary-plist decoder, not the ineffective `eventMsgProc` GOT hypothesis in RC1. It retains HU-owned `showUI/stopUI` and `updateViewArea` commands, observes the stock phone sender, and implements a bounded 150-ms fallback/replay. The separate RC2 application package was built from this corrected source and tested **offline only**. There is **no recorded iPhone UI completion or vehicle acceptance for v0.5**.

Read [control-plane design](docs/ax1800m/CONTROL-PLANE.md), [test matrix](docs/ax1800m/TEST-MATRIX.md), [known issues](docs/ax1800m/KNOWN-ISSUES.md) and [compatibility/recovery](docs/ax1800m/COMPATIBILITY-AND-RECOVERY.md).

## Identity and recovery boundary

The owner-observed Mini Ultra 1-B sample reports `AX1800M/suding/v851se-yunlian-cp`, system `202603120956CA`, and after the October OTA protocol `20261008165747`. Exact stock catalog `ax_202610081657`, executable SHA-256 `edff2ce4ae238d682fdc45be680d4cab919fc1be09bf398aaff4897289390bcb`. Retail product names do not establish PCB/boot-ROM equivalence. An application rollback only works if the updater remains reachable; no complete hard-brick recovery is proven.

The [read-only checker v0.2 instructions](PROBE-README.md) cover the studied pre-/post-October identities but do not authorize firmware installation. Third-party vendor binaries in release archives are proprietary inputs; the source MIT license does not relicense them. Owner-authorized photographs in the source tree are not MIT-licensed.
