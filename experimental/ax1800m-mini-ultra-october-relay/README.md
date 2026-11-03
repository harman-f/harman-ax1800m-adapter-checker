# Carlinkit MINI Ultra 1-B — AX1800M October relay v0.5 experimental source

**EXPERIMENTAL; NOT HARDWARE-QUALIFIED; NO UNIVERSAL FLASH COMPATIBILITY.** This fork contains an independently developed source candidate for the exact October `sdDongle` baseline. The v0.4 contribution remains preserved in upstream commit history and in the merged [upstream PR #1](https://github.com/RandomGenerated543/harman-ax1800m-adapter-checker/pull/1).

## Validated input / owner-reported sample

| Characteristic | Required observed value |
|---|---|
| Platform / customization | `AX1800M` / `suding` |
| Product | `v851se-yunlian-cp` |
| Tested system version | `202603120956CA` |
| Observed protocol version | `20261008165747` after October OTA |
| OTA catalog name | `ax_202610081657` |
| Pinned stock TAR SHA-256 | `13ca438ad4db00bbac0fa4650419df110bf17611a69525409261318a8bbade86` |
| Pinned stock sdDongle SHA-256 | `edff2ce4ae238d682fdc45be680d4cab919fc1be09bf398aaff4897289390bcb` |

These identify one owner's labeled *Mini Ultra 1-B*, not all devices sold under that retail name. **Never install based on the product name alone.** A manufacturer's OTA offer does not independently prove a matching executable or recoverability.

## What changed since source v0.4

The v0.4 independent Type-111 dual-screen video relay and selective teardown treatment remain in place. The **v0.5** branch adds a narrow HU→phone command-plane observer/bridge to address a user-observed mismatch: MHI2 map style, ETA and maneuver settings work over direct USB but apparently do not update the iPhone's wireless cluster presentation.

- Guard the exact October HU event processor and phone-side `AirPlayReceiverSessionSendCommand` GOT slots before activating new observation hooks.
- Preserve stock forwarding first; add one conditional resend for supported `showUI`, `stopUI`, `updateViewArea` if there was no successful synchronous stock submission.
- Retain the latest exact HU-owned show/stop and view parameters; use a bounded cache and replay them on the next phone Type-111 session, without overwriting the car's choice with the old fixed URL.
- Respect the car's validated second-display `initialURL` as startup default where present.
- Log only command names and known view/ETA/speed/compass/maneuver enums; full URLs, UUIDs and personal/phone identifiers are excluded from this new trace.

**Limitations:** The user has not yet tested v0.5 on hardware. A synchronous send result is not an iPhone acceptance ACK. The source does not solve the independently observed ~30-second keepalive timeout or `port_valid=0` reconnect failure. Async completion, long-session ownership and real-world command ingress remain to be qualified. v0.5 is a **candidate, not a verified fix**.

## Offline source build and tests

Requirements: Zig **0.14.1**, Python 3, a working POSIX C compiler for tests, pthreads (Linux/macOS/WSL). On Linux:

```sh
ZIG=/absolute/path/to/zig HOST_CC=cc python3 build.py
```

The command builds a MIPS32r2 shared library and runs host mock suites for relay lifecycle, URL validation and geometry. It does **not** build a firmware OTA TAR or contact the adapter. The associated fork release workflow validates the exact stock input, guarded executable patch, candidate TAR, unchanged vendor companion libraries, checksum manifest and a local-only uploader dry-run before publishing a test prerelease.

## Firmware test releases and rights

Firmware/rollback archives, when published, contain third-party manufacturer binaries. The source license **does not** apply to, grant rights over or relicense those binaries; inspect applicable vendor terms before redistribution or installation. The firmware test prerelease is not a production firmware or warranty of recovery. See the repository's firmware download page and the release's `START-HERE.md` and `RECOVERY.md` before considering installation.

The two owner-supplied photographs below were permitted for this repository's publication only. They are **not MIT-licensed**; reuse requires the owner's permission.

![Owner-permissioned Mini Ultra 1-B packaging photo](assets/miniultra1-b-packaging-photo.jpg)

![Owner-permissioned Mini Ultra 1-B dongle and packaging photo](assets/miniultra1-b-package-and-dongle-original.jpg)

## Provenance

This v0.5 source is developed from the MIT-licensed independent relay v0.2 → v0.4 work and incorporates ABI and helper lineage from [OMKE/wireless-carplay-virtual-cockpit](https://github.com/OMKE/wireless-carplay-virtual-cockpit) (reference commit `321191526ef26f98df87d85cd35d7597e5940ff1`). Preserve [LICENSE](LICENSE) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). The source references a pinned proprietary October firmware for ABI research; the vendor binaries remain proprietary.

For development details and offline-gate evidence see [CaneTLOTW/M.I.B._Research draft PR #154](https://github.com/CaneTLOTW/M.I.B._Research/pull/154) (private research; may require access).
