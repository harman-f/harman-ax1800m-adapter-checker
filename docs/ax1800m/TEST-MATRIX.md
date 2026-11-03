# Evidence and test matrix — AX1800M relay

**Snapshot:** 2026-11-03, experimental source v0.5. `PASS` requires a completed CI job or actual test artifact; no hardware result is inferred from compilation.

| Function / gate | v0.4 vehicle observation | v0.5 offline proof | v0.5 on AX1800M |
| --- | --- | --- | --- |
| Stock main-screen/Type-110 preserved | Main UI visible in reported session | Mock regression PASS | Not independently checked |
| Dedicated Type-111 cockpit video | CarPlay video, navigation symbols, zoom reported; one run 6,827 frames | Relay lifecycle and frame mocks PASS | **Not tested** |
| Partial receive timeout, socket errors | Keepalive disconnect still occurred | Frame/timeout/error regression PASS | Not tested for new build |
| Native-only vs auxiliary-only/full teardown | Earlier menu exit and later 30-s drop reported | Teardown classification + stale-generation tests PASS | Not tested |
| HU `initialURL` instead of fixed startup URL | Not demonstrated for new code | Profile parser + mock input PASS | **Not tested** |
| HU `showUI`/ETA/map/maneuver ingress | Works by USB; wireless apparently stale | Corrected MIPS callsite audit + mocked parser | **Not observed with v0.5** |
| Stock phone sender, 150-ms delayed fallback | No phone command logs proving delivery | Host tests for stock-first/no duplicate and one-shot fallback PASS | **Not tested** |
| Two-slot UI/ViewArea cache, stopUI, stale revisions | None | Host tests PASS | **Not tested** |
| Reconnect/replay to new phone generation | Sporadic disconnect / port invalid reported | Source state tests PASS | **Not tested** |
| Source compile for MIPS32r2/o32 | Prior firmware build exists | Zig 0.14.1 cross-build PASS | Loader/ELF runtime unverified |
| iOS command ACK and cockpit visual update | Wired A/B reference only | No host proof possible | **Unverified** |
| Full OTA package, flash and recovery | Previous historical packages only | **RC2 TAR and ZIP offline PASS; CGI uploader mock PASS** | **Not installed, flashed or recovery-tested** |

The [source-only workflow](../../.github/workflows/ax1800m-v05-offline.yml) runs the C host relay, URL and geometry tests, AddressSanitizer/UBSan for the first two, downloads the **SHA-256 pinned** Zig 0.14.1 toolchain, cross-builds a MIPS shared object, checks the publication manifest and does no target action. The Research development precursor passed a host/MIPS check, but **the public fork's own CI is the authoritative gate for the published bytes**; inspect Actions before quoting its result.

The host mocks do not simulate a full adapter worker on target, actual HTTP plist event receive, Wi-Fi stack, Bluetooth, iOS, video decoder, radio dropout, or hardware-loader ABI. **Do not market the current state as “wireless menu fixed”.**

## Minimum parked-vehicle acceptance

1. Baseline: confirm ETA `yes → no → yes` and surface `base → map` work with direct USB, keeping the same HU configuration.
2. With the separately reviewed, explicitly opted-in v0.5 RC2 test package, repeat wirelessly while Stream 111 stays alive. Correlate *matching* `hu_cmd_ingress`, `phone_cmd_submit` or `hu_cmd_delayed`, a current phone session, and the cockpit visual result.
3. Check `stopUI` on leaving the menu, and disconnect/reconnect twice. Verify latest rather than stale UI is replayed, and Type-110 continues.
4. Separately observe at least 60 seconds after screen teardown and the next reconnect; capture keepalive and `port_valid` outcome. Do not conflate failure modes.

No in-car v0.5 acceptance is recorded. Explicit review and a known rollback plan are required before any package is installed.
