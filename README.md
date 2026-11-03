# Wireless CarPlay adapters: checker, historic images and AX1800M relay

**Experimental research. Source builds are not installable firmware.** Incorrect OTA images can disable an adapter. Read [compatibility and recovery limitations](docs/ax1800m/COMPATIBILITY-AND-RECOVERY.md) before attempting any update.

## Find the right component

| Component | Contents | Verified status |
| --- | --- | --- |
| [AX1800M Mini Ultra 1-B independent relay v0.5](experimental/ax1800m-mini-ultra-october-relay/README.md) | Source, host regression tests, MIPS32r2 build recipe; **no firmware TAR or flasher** | Offline build/tests; **v0.5 has not been run on hardware** |
| [Read-only AX1800M identity checker](PROBE-README.md) | Read-only Python probe and [checker ZIP](Harman-AX1800M-readonly-probe-v0.1.zip) | Strict allowlist for pre-October-OTA protocol `20260109175612`; does not update |
| [Legacy experimental firmware packages](ADAPTER-FIRMWARE.md) | Two separately pinned, previously published ZIPs for **different** hardware/version targets | Individual, historic qualification only; **not** v0.5 |
| [HW301 / CXZ521 / SEAT MU1409 package](HW301-CXZ521-SEAT-MU1409-v0.1.zip) | Legacy v0.1 candidate and its own rollback/uploader | Hardware-specific; not interchangeable with AX1800M |
| [AX1800M / Suding / Leon MU1447 v0.2 package](AX1800M-Suding-Leon-MU1447-October-v0.2.zip) | Legacy v0.2 candidate and its own rollback/uploader | Pinned older **system** version; not a Mini Ultra v0.5 build |

## AX1800M v0.5 engineering focus

The direct USB connection between MHI2 and iPhone already applies the cockpit's Apple Maps URL/menu settings. Through a wireless AX1800M dongle the Type-111 video stream has been observed, but **changes to ETA, map surface and maneuver position do not reliably appear**. A dongle terminates the car-facing and iPhone-facing sessions, so working video does not establish a working control bridge.

v0.5 instruments the **actual HU binary-plist decoder** (not the ineffective eventMsgProc GOT reference), observes the stock phone command sender, retains the latest HU-owned `showUI/stopUI` and `updateViewArea`, and offers a bounded delayed submission and next-phone-session replay. It prefers the HU's `initialURL` to the prior constant fallback. This is source-level behavior: **no vehicle, phone ACK, OTA installation or reconnect fix is claimed for v0.5**.

Start here: [AX1800M documentation index](docs/ax1800m/README.md), [control-plane design](docs/ax1800m/CONTROL-PLANE.md), [test/evidence matrix](docs/ax1800m/TEST-MATRIX.md), and [open bugs](docs/ax1800m/KNOWN-ISSUES.md).

## Device identification and safety

- The studied owner-supplied *Mini Ultra 1-B* sample is `platform=AX1800M`, `custom=suding`, `product_Model=v851se-yunlian-cp`, `system_version=202603120956CA`. Following October OTA, protocol was observed as `20261008165747`; the earlier checker targets `20260109175612`.
- The experimental source specifically targets October `sdDongle` catalog `ax_202610081657`, pinned by **exact binary hash and entry-point ABI**. The retail model name alone cannot establish compatibility.
- No current package here is a tested AX1800M v0.5 OTA or full hard-brick recovery image. Do not transplant the old ZIPs or bypass identity checks.

Source license and photo rights are explained [here](experimental/ax1800m-mini-ultra-october-relay/README.md#license-and-publication-scope).
