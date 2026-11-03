# AX1800M Mini Ultra1B — v0.5 RC1 TEST RELEASE

**EXPERIMENTAL • NOT TESTED ON THE TARGET DONGLE • NOT A GENERAL FIRMWARE UPDATE**

This ZIP contains an October `ax_202610081657` application candidate and exact October application rollback, a guarded local uploader, source snapshot, and reproducibility receipt. It is for a specific owner-tested hardware/software family only.

## Identity checks before ever considering installation

- Platform `AX1800M`, customization `suding`, product `v851se-yunlian-cp`
- Owner sample system `202603120956CA`; exact vendor executable must be independently checked
- Permitted protocol versions of the guarded uploader: `20260109175612` and `20261008165747`
- Stock TAR SHA-256: `13ca438ad4db00bbac0fa4650419df110bf17611a69525409261318a8bbade86`

**Do not flash based only on retail labeling, hardware family or firmware version text.** The updater does not check the running ELF hash itself. A normal CGI response is not proof that the newly built relay started successfully.

## Local, no-write verification

```sh
python3 adapter.py dry-run
```

Optional GET-only device identity check (contacts the adapter without changing it):

```sh
python3 adapter.py probe --host 192.168.50.100
```

`check-only` is **not** read-only: it uploads all chunks into temporary updater storage. `flash` and `rollback` perform changes and request a reboot. Never run them without explicit operator review of device compatibility and recovery availability. The bundle's Python helper does not run network actions on its own.

## What changed

The v0.5 source implements conditional HU→phone `showUI` forwarding and retained HU-specified map/ETA/maneuver URLs across phone Type-111 session reconnect, plus privacy-bounded diagnostics. It preserves a remembered `stopUI` and prefers the car's `initialURL` to the older fixed default. These are **offline-tested source features only**. Not demonstrated with an iPhone or cockpit on this binary.

**Unresolved:** ~30-second keepalive timeout after teardown, `port_valid=0` on a subsequent connection, target loader/init and async iOS completion, possible recovery beyond application OTA. These are reasons not to advertise this as stable.

## Files

- `firmware/ax_independent_relay_v05.tar` — candidate application TAR, **not a whole-device image**
- `firmware/ax_202610081657_stock_rollback.tar` — exact October stock application rollback, **not full boot/flash recovery**
- `IMAGES.json` and `MANIFEST.json` — candidate/rollback hashes and every package file hash
- `BUILD-RECEIPT.json` — source/toolchain/input provenance
- `adapter.py` — operator-controlled uploader with exact identity and CGI acknowledgement gates
- `RECOVERY.md` — rollback limitations
- `source/` — associated MIT project source, tests and licenses

The included manufacturer files are proprietary, and **are not relicensed by the project's MIT license**. Check rights/terms before redistribution.

**Do not treat this prerelease as a successful vehicle test.**
