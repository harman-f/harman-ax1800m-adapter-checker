# AX1800M independent relay source history

| Source stage | Change | Qualification |
| --- | --- | --- |
| v0.2 (Oct 2026) | Independent video-111 relay experiments and SETUP; earlier source/artefacts retained separately | Selected device tests; not stable |
| v0.3 (Oct 2026) | Initial SETUP, cancellation and lifecycle fixes | Host checks; previously observed disconnects |
| v0.4 (Nov 1, 2026) | Corrected stock `relay_teardown` ABI: receives request **dictionary**, not streams array; preserve native-only/mixed teardown, timeout read and worker generation | Host suite; owner-reported video session, keepalive still unresolved |
| **v0.5 (Nov 3, 2026)** | Corrected HU plist decoder hook (direct `eventMsgProc` call invalidates earlier GOT assumption); phone send tracing, 150-ms one-shot fallback, two-slot HU UI/ViewArea cache, phone-session replay, HU `initialURL`, safe parameter parsing and CI | **Source plus separately packaged experimental RC2 application ZIP; offline host/MIPS/installer-mock gates only, no v0.5 vehicle acceptance.** |

The open-source v0.4 upstream merge, [PR #1](https://github.com/RandomGenerated543/harman-ax1800m-adapter-checker/pull/1), is history, not proof of v0.5 target compatibility. New source changes should be reviewed in a **separate** follow-up PR; a merged PR cannot be “updated” to carry later code. This project does not merge or redistribute proprietary vendor firmware as part of the source change.

Current public downloads are intentionally limited to v0.5 RC2 and checker v0.2. Historic source-stage names in this log are provenance, not links to obsolete installation packages. See [stock vs v0.5](STOCK-VS-V05.md).
