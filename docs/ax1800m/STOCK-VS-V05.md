# October stock vs experimental AX1800M v0.5 RC2

**Scope:** Owner-studied Mini Ultra 1-B (`AX1800M` / `suding` / `v851se-yunlian-cp`; system `202603120956CA`) and the exact October stock application build. The v0.5 RC2 archive contains an **application-level patch**, not full vendor firmware. These statements do **not** apply to every device sold as AX1800M.

## Feature and behavior delta

| Function | October stock application (baseline) | Independent relay v0.5 RC2 | Evidence / caveat |
| --- | --- | --- | --- |
| Main infotainment CarPlay / Type 110 | Existing vendor wireless CarPlay path | Retained, not replaced by the new Type-111 worker | Stock function; v0.5 host regression only |
| Cockpit Type-111 video | No validated independent Type-111 relay in the studied unmodified stock application | Additional Type-111 session/worker, frame forwarding and independent lifecycle | Earlier customized v0.4 vehicle video observed; RC2 device test **pending** |
| HU-owned map/ETA/maneuver commands | Vendor HU plist handler and phone sender exist; wireless dynamic menu updates appeared stale in owner observations | Observe the actual HU binary-plist decoder and stock phone sender; capture qualified `showUI`, `stopUI`, `updateViewArea` | This is an additional instrumented path, **not** proof stock never sent a command |
| Dynamic `showUI` options | Direct USB to iPhone applies requested ETA/map/maneuver options; wireless stock behavior not established as equivalent | Retain validated current HU URL and nested parameters instead of relying only on fixed startup `/map` | Parser and state tested on host; iPhone visual application **unverified** |
| Missing command fallback | No v0.5-style delayed fallback in the studied stock binary | Prefer stock forwarding, then one bounded fallback after at least 150 ms if submission was not observed | Host behavior only; return code is submission, **not** iOS acknowledgment |
| New phone session / menu replay | No verified HU-owned latest-UI/ViewArea replay for the studied stock path | Cache latest UI and ViewArea, honor `stopUI`, replay on new Type-111 phone generation; use HU `initialURL` if valid | Host tests; wireless reconnect and visual redraw **unverified** |
| Receive, cancellation and teardown | Vendor Type-110 behavior remains the base | Independent relay guards generations, partial reads, and auxiliary/native teardown | Tests pass on host, not evidence of fixed transport teardown |
| Keepalive / reconnect / Wi-Fi / Bluetooth | Sporadic timeout and `port_valid=0` observed during previous modified-device sessions; stock root cause undetermined | **No transport-stack or keepalive fix included** | Existing P1 defects remain open; do not attribute root cause to stock or declare fixed |
| Diagnostics | Existing vendor logs | Added privacy-reduced command-stage markers, allowlisted enum options and sender return codes | Does not log full URLs, UUIDs or arbitrary plist in new markers |
| Update / recovery | Vendor October application is the rollback reference | Separate guarded updater and application TAR; exact stock-app rollback included | Mocked updater tests only; no proof of bootloader/hard-brick recovery |

## What is actually tested

**Observed before RC2:** Earlier customized v0.4 sessions carried cockpit CarPlay video; direct USB applied the relevant navigation menu settings. The historical keepalive timeout and invalid reconnect port were not resolved.

**Verified offline for RC2:** relay/teardown and command-state host suites, navigation-URL parser, geometry tests, ASan/UBSan, MIPS32r2 cross-build, pinned stock patch checks, application packaging and mocked updater paths. The checker v0.2 has separate Python 3.9/3.12 offline tests.

**Not verified on the target:** RC2 flash, real HU command ingress, iPhone acceptance/visual redraw, reconnect/replay timing, 60-second teardown keepalive window, repeated reconnect, or recovery after an unreachable adapter.

## Boundaries for a controlled vehicle trial

First run read-only checker v0.2 and inspect the identity report; it never authorizes flashing. Independently compare the complete stock binary identity/ABI and document a recovery path before deciding to install. In a parked test, compare USB and wireless navigation settings (`showETA`, map surface, maneuver position), capture command-stage logs, verify actual cockpit UI updates, leave the screen, watch keepalive for at least 60 seconds and reconnect twice. Distinguish missing ingress, unsuccessful sender submission and a phone that does not redraw.

More detail: [CONTROL-PLANE.md](CONTROL-PLANE.md), [TEST-MATRIX.md](TEST-MATRIX.md), [KNOWN-ISSUES.md](KNOWN-ISSUES.md), [COMPATIBILITY-AND-RECOVERY.md](COMPATIBILITY-AND-RECOVERY.md).
