# Adapter firmware downloads, provenance and limitations

**HIGHLY EXPERIMENTAL — NO WARRANTY.** Firmware can disable a dongle. Release assets modify the adapter, not the MHI2 or virtual cockpit. No automatic compatibility or hard-brick recovery is implied.

## Current AX1800M Mini Ultra1-B candidate

[**v0.5 RC2 — experimental GitHub prerelease**](https://github.com/harman-f/harman-ax1800m-adapter-checker/releases/tag/ax1800m-miniultra-v0.5-rc2): application candidate `ax_independent_relay_v05_rc2.tar`, exact October application rollback, guarded Python updater, corresponding source snapshot, offline test receipts and SHA-256 manifest.

It targets the owner-reported `AX1800M` / `suding` / `v851se-yunlian-cp`, system `202603120956CA`, with pinned stock October catalog `ax_202610081657` and stock `sdDongle` SHA-256 `edff2ce4ae238d682fdc45be680d4cab919fc1be09bf398aaff4897289390bcb`. These are not universal compatibility claims. The actual installed executable/hook ABI must be confirmed separately.

**Qualification:** v0.5 corrected the HU→iPhone `showUI` control-hook approach (actual HU plist decoder, stock-first send, bounded delayed fallback, HU-owned `initialURL` and replay). CI passed Linux host, sanitizer, Zig MIPS cross-build, exact stock patch preimages, application TAR, release ZIP, 23 mocked CGI/updater tests and network-free `dry-run`. **It has not been installed or tested on the actual dongle or with an iPhone.** Separate keepalive and `port_valid=0` reconnect defects remain open.

Start with `python3 adapter.py dry-run` inside the extracted RC2 ZIP. That command is offline and safe. `probe` is GET-only identity lookup. **`check-only` is not read-only**; it uploads chunks into temporary updater storage. `flash` and `rollback` mutate the target and request reboot. Only run those after an explicit supervised compatibility/recovery review. The OCT stock rollback is **not** full bootloader recovery.

## Public distribution policy

Only the current experimental v0.5 RC2 application package and read-only checker v0.2 are offered as public downloads. Older test releases were superseded or targeted incompatible system/board variants; they are **not installation candidates**, and historical Git tags are retained for source provenance only. Archived release assets must not be confused with the current Mini Ultra 1-B system.

Consult the [stock-versus-v0.5 comparison](docs/ax1800m/STOCK-VS-V05.md) for an explicit feature-by-feature delta and unchanged defects. RC2 still has no hardware qualification and no proven hard-brick recovery.
## Copyright, source and evidence

The current [AX1800M source](experimental/ax1800m-mini-ultra-october-relay/README.md) is published under its MIT/third-party source notices; its directory contains **no vendor TAR, patched binary or updater**. Separate downloadable RC2/legacy ZIPs contain proprietary manufacturer application binaries, which are **not relicensed** by the source license. Review the vendor's distribution terms before sharing or installing.

Research lineage includes [OMKE/wireless-carplay-virtual-cockpit](https://github.com/OMKE/wireless-carplay-virtual-cockpit) and for the unrelated HW301 design [kamgurgul/mib2q-carplay](https://github.com/kamgurgul/mib2q-carplay). See [full release index](docs/ax1800m/RELEASES.md), [testing](docs/ax1800m/TEST-MATRIX.md) and [recovery](docs/ax1800m/COMPATIBILITY-AND-RECOVERY.md).
