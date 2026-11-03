# Firmware and tool downloads — GitHub Releases

Downloadable ZIPs are now **GitHub Release assets**, not versioned in the repository root. The historical firmware ZIP bytes were preserved unchanged, with matching SHA-256 checksums.

| Role | Release | ZIP SHA-256 |
| --- | --- | --- |
| **Current test firmware, NOT vehicle qualified** | [AX1800M Mini Ultra1-B v0.5 RC2](https://github.com/harman-f/harman-ax1800m-adapter-checker/releases/tag/ax1800m-miniultra-v0.5-rc2) | `11ac93b88c65849f8ed3517ca7cbbe0bd93818f881034e9aca8abf853fbc407a` |
| **SUPERSEDED — do not install** | [AX1800M v0.5 RC1](https://github.com/harman-f/harman-ax1800m-adapter-checker/releases/tag/ax1800m-miniultra-v0.5-rc1) | `3466c105a8add4f6e6eee7c8ef6e285d5d7c2cb6273283390e0c533a4a3e7044` |
| Archived, older AX1800M system | [AX1800M Leon MU1447 October v0.2](https://github.com/harman-f/harman-ax1800m-adapter-checker/releases/tag/ax1800m-leon-mu1447-v0.2-legacy) | `b24600fea982667e896580b7b19e1712de96249da260cf5cb5f5f8ae33fcd1d6` |
| Archived, different hardware | [HW301/CXZ521 SEAT MU1409 v0.1](https://github.com/harman-f/harman-ax1800m-adapter-checker/releases/tag/hw301-seat-mu1409-v0.1-legacy) | `89c936f5b6d4010d02570b069e1ee05c52b80a5e0229a3334183b95163f00579` |
| Read-only diagnostic, **not firmware** | [AX1800M checker v0.1](https://github.com/harman-f/harman-ax1800m-adapter-checker/releases/tag/ax1800m-readonly-checker-v0.1) | `8fc4d6aa1f93c67ec06fb140649ecac9029275cf9e72653c4fc4500b4592f569` |

## v0.5 RC2 contents

The RC2 ZIP includes the newly built `ax_independent_relay_v05_rc2.tar` application image, exact October stock application rollback, a guarded Python updater, source snapshot, manifest and build receipt. Additional Release assets provide `SHA256SUMS.txt` and `BUILD-SUMMARY.json`. The [RC2 GitHub Actions build](https://github.com/harman-f/harman-ax1800m-adapter-checker/actions/runs/41601507775) passed source/host tests, ASan/UBSan, MIPS32r2, the pinned stock patch, OTA archive integrity and mocked uploader tests.

**None of that proves correct operation on the Dongle.** There is no recorded RC2 iPhone UI ACK, live menu switching, boot/recovery qualification or hard-brick recovery. An HTTP-based rollback requires a working updater. Installation can disable the adapter. The actual hardware/ELF/ABI must be inspected before flashing.

RC1 was superseded after discovering the vendor's HU event processor is invoked by a **direct MIPS call** rather than the GOT entry originally intercepted. RC2 was rebuilt from the newer `main` source with the corrected HU binary-plist decoder hook and delayed stock-first fallback.

Vendor firmware binaries distributed in application archives remain proprietary. Source licensing does not relicense them. See [compatibility and recovery](COMPATIBILITY-AND-RECOVERY.md), [test matrix](TEST-MATRIX.md) and [firmware provenance](../../ADAPTER-FIRMWARE.md).
