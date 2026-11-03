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

## Three independent deliverables

**1. Read-only checker:** `probe-adapter.py` and old checker ZIP strictly accept the earlier protocol `20260109175612`; an adapter already on the October OTA may be rejected by this older checker. That rejection is **not** proof of failure or incompatibility. Do not bypass the allowlist to install firmware.

**2. Historical hardware-specific ZIPs:** The HW301/CXZ521 and AX1800M/Leon MU1447 v0.1/v0.2 packages are older, differently pinned firmware experiments with their own rollback/updaters. Their included binaries remain unchanged; they are **not** Mini Ultra v0.5 builds and cannot be transplanted.

**3. Current independent v0.5:** A source directory. `build/libSdHOct.so` is a development shared object, **not** a complete install image, updater or rollback package. Source compile and host tests do not establish safe loader behavior.

## Before any future installation

Confirm model, running system/protocol, stock OTA archive SHA-256, actual `sdDongle` SHA-256, expected library imports/hook slots, target boot path, exact installer behavior, rollback and power-loss failure modes. Test on a parked vehicle with a retained recovery plan, never by experimenting with the two old ZIPs or overriding checks.

An HTTP-based firmware rollback cannot rescue a device that no longer boots enough to provide the updater. There is **no verified full hard-brick USB/boot-ROM recovery procedure** for the studied PCB in this repository. Avoid claiming one based on an unconfirmed chip family.

See [ADAPTER-FIRMWARE.md](../../ADAPTER-FIRMWARE.md) for historic binary package hashes and [PROBE-README.md](../../PROBE-README.md) for the old checker scope.
