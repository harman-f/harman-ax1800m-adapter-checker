# Compatibility, downloads and recovery boundary

## Known studied sample — not a compatibility whitelist

| Property | One owner-observed Mini Ultra 1-B |
| --- | --- |
| Web platform/custom/model | `AX1800M` / `suding` / `v851se-yunlian-cp` |
| System | `202603120956CA` |
| Protocol *before* October OTA | `20260109175612` (read-only checker allowlist) |
| Protocol *after* October OTA | `20261008165747` |
| Expected stock catalog | `ax_202610081657` |
| Stock TAR size and SHA-256 | 1,812,992 bytes / `13ca438ad4db00bbac0fa4650419df110bf17611a69525409261318a8bbade86` |
| Analyzed stock `sdDongle` SHA-256 | `edff2ce4ae238d682fdc45be680d4cab919fc1be09bf398aaff4897289390bcb` |
| HU used in owner report | Skoda MHI2 `MHI2_ER_SKG13_P4526_MU1440` |

The product string `v851se` and the retail name alone cannot establish a SoC, boot ROM, USB recovery device, hardware revision or flash layout. The exact ELF hash and relevant GOT pointers are preconditions for this source. The matching vendor binary and stock TAR are **not distributed** in the source directory.

## Two current, independent deliverables

**1. Read-only checker v0.2:** `probe-adapter.py` recognizes the studied pre-October `20260109175612` and October `20261008165747` protocols, records identity and reports an *assessment*, never permission to flash. `install_authorized` is always false: an HTTP version string cannot verify stock ELF hash, board/bootloader revision, runtime ABI, the installed archive or recovery.

**2. Experimental v0.5 RC2 application:** The [source directory](../../experimental/ax1800m-mini-ultra-october-relay/README.md) contains no proprietary firmware. A separate [RC2 test prerelease](https://github.com/harman-f/harman-ax1800m-adapter-checker/releases/tag/ax1800m-miniultra-v0.5-rc2) supplies the offline-verified application TAR, guarded updater and matching October *application* rollback. It is **not** whole-device factory firmware, proof of safe loader operation or completed vehicle acceptance.

Older binaries targeted different boards and system revisions and must never be treated as interchangeable with the current Mini Ultra 1-B. There are no maintained public downloads for those builds. The exact functional difference from stock is in [STOCK-VS-V05.md](STOCK-VS-V05.md).
## Before any future installation

Confirm model, running system/protocol, stock OTA archive SHA-256, actual `sdDongle` SHA-256, expected library imports/hook slots, target boot path, exact installer behavior, rollback and power-loss failure modes. Test on a parked vehicle with a retained recovery plan, never by experimenting with the two old ZIPs or overriding checks.

An HTTP-based firmware rollback cannot rescue a device that no longer boots enough to provide the updater. There is **no verified full hard-brick USB/boot-ROM recovery procedure** for the studied PCB in this repository. Avoid claiming one based on an unconfirmed chip family.

See [ADAPTER-FIRMWARE.md](../../ADAPTER-FIRMWARE.md) for current package provenance and [PROBE-README.md](../../PROBE-README.md) for the checker scope.
