# Known issues and unresolved investigations

Scope: Mini Ultra 1-B / AX1800M Suding / pinned October binary, independent v0.5 **source**. All issues here remain **open unless independently evidenced**.

| Priority | Symptom / unresolved question | Evidence, interpretation and next gate |
| --- | --- | --- |
| P1 | **Wireless cockpit map settings appear stale** after changing ETA, map style/surface or maneuver position | Direct USB applies the same menu choices. Earlier dongle logs lack the actual HU-originated command and iPhone confirmation. v0.5 adds the corrected HU ingress, sender observation and bounded fallback; its effect is **not field-tested**. |
| P1 | **Keepalive timeout after leaving the screen** | Owner-reported v0.4 session forwarded 6,827 frames; about 30 s after screen teardown an independent keepalive timer expired. Source-level teardown classification was corrected in v0.4; this alone did not establish keepalive root cause. |
| P1 | **Reconnect can fail with `port_valid=0`** | Following the timeout, a new HU setup lacked a valid port. Not proven whether stale generation, HU/phone session teardown or new transport setup was responsible. Needs log correlation and recovery test; do not assume v0.5 UI control code fixes it. |
| P2 | **Phone command accepted but no visible redraw** | `AirPlayReceiverSessionSendCommand` returning zero confirms submission, not an iOS visual/UI completion. Even retransmitting the same URL can be insufficient in some third-party implementations. Need target-specific response and actual cockpit observation. |
| P2 | **Out-of-order commands or rapid ETA toggles** | Latest-value cache, generation guards and delayed fallback are present. Stock event completion and phone redraw order have not been measured on device. |
| P2 | **Reconnection replay timing/async ownership** | UI/ViewArea replay happens on new Type-111 setup. No callback ACK, bounded asynchronous retry policy or full reconnect acceptance has been established; do not claim exactly-once delivery. |
| P2 | **Other adapter firmware/board revisions** | Retail label and product model do not prove identical ELF, GPIO/flash or bootloader. Hook offsets pinned to one October stock hash; fail closed on mismatched GOT, no universal firmware. |
| P2 | **Recovery after a truly inaccessible adapter** | Web OTA and application rollback work only while the required interfaces are alive. A complete UART/boot-ROM/hard-brick procedure for the exact PCB is not proven. |

## How to isolate the command problem

**Ingress missing:** no `hu_cmd_ingress` for a proven USB-working toggle. Confirm the pinned app/hash and that the event actually arrives through the decoded HU-plist HTTP route before trying unrelated MHI2 menu edits.

**Ingress present, egress missing:** check `hu_cmd_cache` and `hu_cmd_delayed`; verify matching Type-111 UUID and active session. A `submit_rc` error is not iOS rejection proof.

**Egress with zero return, no visual effect:** check actual phone session, display descriptor UUID, `initialURL`, dynamic URL values, and app redrawing. Observe `stopUI`/ViewArea ordering. Do not substitute a `suggestUI` phone→HU HTTP 422 diagnosis: it runs in the opposite direction.

**Reconnect failure:** collect separate teardown, keepalive and `port_valid` timelines; do not merge this with an ETA URL investigation until causal evidence exists.

Reference: [CONTROL-PLANE.md](CONTROL-PLANE.md) and [TEST-MATRIX.md](TEST-MATRIX.md).
