# Type-111 control plane: what USB has that the wireless AX1800M must relay

## Direct USB (known-working reference)

```text
MHI2/MU1440 custom navigation menu → GEN2 URL composer
    → AirPlayReceiverSessionSendCommand(showUI, params.url=current)
    → directly connected iPhone → new cluster map/ETA/layout
```

When connected by USB, the owner's ETA/map-style/maneuver changes update the cockpit. That is the user-provided reference. No redesign of the HU Java menu or GEN2 URL grammar is part of this AX1800M work.

## Wireless bridge and command directions

```text
CAR/HU side                   AX1800M (October sdDongle)                   PHONE side
HU HTTP/plist event  → parser → vendor eventMsgProc → phone AirPlay sender → iPhone
                  \                       Type-111 worker → video relay ← phone
                   \ v0.5 captures/retains UI command and checks sender submission
```

The **video** channel 111 and **control** channel are distinct. Working frames, camera symbols or zoom do not prove that a later car-originated `showUI` reaches the same phone generation. `suggestUI` is a **phone→HU** suggestion; an HTTP 422 in that path is not evidence that a HU-originated `showUI` was rejected.

## Exact pinned MIPS code seam

The published source is pinned to October `sdDongle` SHA-256 `edff2ce4ae238d682fdc45be680d4cab919fc1be09bf398aaff4897289390bcb`.

| Callsite / symbol | Address | How it is called |
| --- | --- | --- |
| HU event HTTP worker / plist decode | call at `0x424390`, return-PC `0x424398` | `jalr` via GOT `0x565178` → `CFBinaryPlistV0CreateWithData` `0x49ba74` |
| Vendor event processor | call at `0x4243dc` | **Direct `bal 0x438354`** to `eventMsgProc`; changing GOT `0x5655d8` would not intercept that call |
| Phone CarPlay command sender | `0x472650` | `jalr` via GOT `0x565848` → `AirPlayReceiverSessionSendCommand` |

v0.5 replaces the *verified* plist-decoder GOT entry and filters on the specific return-PC; it never modifies the original plist result. It also observes the phone sender and requires both exact stock GOT values before enabling these optional hooks. This corrected ingress supersedes an earlier v0.5 Research draft that incorrectly relied on the event processor's GOT slot.

## Supported presentation commands

The car-originated request is typed `{type, params}` with a UUID qualifying the HU's Type-111 display. The source handles `showUI`, `stopUI`, `updateViewArea` and observes `forceKeyFrame` without logging noisy keyframe traffic.

Known URLs:
```text
maps:/car/instrumentcluster
maps:/car/instrumentcluster/map
maps:/car/instrumentcluster/instructioncard
```

Recognized optional arguments for base/map surfaces: `showETA=yes|no|user`, `showSpeedLimit=yes|no|user`, `showCompass=yes|no|user`, `maneuverLayout=leftAligned|rightAligned|topAligned` (or empty for unspecified). Parsing is bounded to 383 characters, rejects duplicate/unknown keys and never logs the raw URL. Unknown but valid vendor plists continue through stock unmodified.

## v0.5 delivery policy — source behavior, not car-proof

1. Capture the qualified HU plist at the decode boundary, **before stock's direct call** to `eventMsgProc`.
2. Retain the latest exact UI or ViewArea dictionary including a nested copy of `params`, with generation and HU display UUID.
3. Let stock forward normally. When the **same** incoming plist is submitted successfully by stock, cancel pending fallback.
4. Otherwise, after at least 150 ms, one condition-driven worker attempts **one** extra submission through the existing phone session (qualified UUID and still-current generation). This is a bounded, stock-first fallback, not an infinite loop or a guaranteed delivery.
5. At a new Type-111 phone-session setup, replay the latest HU-owned UI then ViewArea; a remembered `stopUI` must not be overwritten by an implicit `showUI`. When there is no remembered HU UI, prefer validated `displays[].initialURL`; only then use historic `maps:/car/instrumentcluster/map` fallback.

**Important limitations:** The stock API return code reports synchronous submission only. No authenticated phone UI completion has been instrumented, and no rule can prove that a later iOS app redraws the screen. 150-ms ordering and session concurrency are source hypotheses requiring target logs. The cache has two slots, so only the latest UI and ViewArea are retained. It intentionally does not modify audio, video encryption, Type-110, iAP2 route guidance or the independent keepalive/teardown issue.

## Privacy-safe log markers

`stage=hu_cmd_ingress` means a known command reached the decoded HU event path; `stage=phone_cmd_submit` means the stock sender returned, not that the iPhone applied it; `stage=hu_cmd_delayed` identifies a bounded fallback; `stage=hu_cmd_replay` is a later session's attempt. Logs may contain the enum surface, ETA/speed/compass/maneuver and result code only. Full URLs, UUIDs and arbitrary plist are never included in these new markers. Do not share raw legacy adapter logs publicly without review.
