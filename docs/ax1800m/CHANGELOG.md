# AX1800M independent relay source history

| Source stage | Change | Qualification |
| --- | --- | --- |
| v0.2 (Oct 2026) | Independent video-111 relay experiments and SETUP; earlier source/artefacts retained separately | Selected device tests; not stable |
| v0.3 (Oct 2026) | Initial SETUP, cancellation and lifecycle fixes | Host checks; previously observed disconnects |
| v0.4 (Nov 1, 2026) | Corrected stock `relay_teardown` ABI: receives request **dictionary**, not streams array; preserve native-only/mixed teardown, timeout read and worker generation | Host suite; owner-reported video session, keepalive still unresolved |
| **v0.5 (Nov 3, 2026)** | Corrected HU plist decoder hook (direct `eventMsgProc` call invalidates earlier GOT assumption); phone send tracing, 150-ms one-shot fallback, two-slot HU UI/ViewArea cache, phone-session replay, HU `initialURL`, safe parameter parsing and CI | **Source-only. Host/MIPS offline gates; no v0.5 vehicle acceptance or OTA.** |

The open-source v0.4 upstream merge, [PR #1](https://github.com/RandomGenerated543/harman-ax1800m-adapter-checker/pull/1), is history, not proof of v0.5 target compatibility. New source changes should be reviewed in a **separate** follow-up PR; a merged PR cannot be “updated” to carry later code. This project does not merge or redistribute proprietary vendor firmware as part of the source change.
