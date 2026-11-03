# AX1800M / Suding read-only Adapter Checker v0.2

**This is a diagnostic tool, not firmware and not an installer.**

Run `probe-adapter.py` with Python 3.9+ while connected to the adapter's own Wi-Fi. The checker sends **only HTTP GET** for `/cgi-bin/getversion.cgi` and, when the device identity matches a documented sample, the root page `/`. It then reads unsolicited SSH/Telnet banners on ports 22 and 23, with **no login, credentials, payload, POST, OTA upload, reboot or configuration write**.

## Download and start

[Latest v0.2 checker release](https://github.com/harman-f/harman-ax1800m-adapter-checker/releases/tag/ax1800m-readonly-checker-v0.2). Release ZIP, its SHA256SUMS file and source live separately from v0.5 RC2 firmware. To run from source, use the version-controlled [probe-adapter.py](probe-adapter.py).

1. Power the adapter independently of the vehicle and connect your computer to the adapter's Wi-Fi.
2. Unzip the v0.2 archive and open a terminal in its folder.
3. On Windows run `py probe-adapter.py`; on macOS/Linux run `python3 probe-adapter.py`.
4. By default the tool checks `192.168.50.100`. If needed use `--host 192.168.x.y`. Only numeric local IPv4 addresses are permitted.
5. Send the resulting `harman-adapter-probe/REPORT.json` and `version.txt`, reviewing any network/serial information before sharing. `web-page.html` may contain private device details.

Optional: `python3 probe-adapter.py --dry-run` verifies argument handling without network access or file creation. `--out OUTPUT_FOLDER` changes the local output folder. It must **not exist** already, so prior diagnostics are never overwritten.

## Recognized version signatures

| Signature | Checker classification | RC2 firmware approval |
| --- | --- | --- |
| `AX1800M/suding`, system `202603120956CA`, protocol `20260109175612` | `pre_october` | **Not applicable** to this running protocol |
| Same platform/custom/system, protocol `20261008165747` | `october_2026` | **Unverified candidate only** |
| Any different/unknown version or product model | `unknown` | **Not authorized** |

If the optional `product_Model` field is reported, it must equal `v851se-yunlian-cp`. Missing model evidence is explicitly recorded and does not strengthen the compatibility assessment.

**A matching version string is insufficient to approve RC2 installation.** The read-only checker cannot access or verify the stock `sdDongle` ELF SHA-256 `edff2ce4ae238d682fdc45be680d4cab919fc1be09bf398aaff4897289390bcb`, the complete stock image, bootloader/board revision, ABI or power-loss recovery. `REPORT.json` always sets `rc2_compatibility.install_authorized=false`. These require independent confirmation. There is no documented proven hard-brick recovery.

## Output, safeguards and testing

The checker saves `version.txt`, `REPORT.json` and—only for recognized identity—`web-page.html`; SSH and Telnet banners are fields of the JSON report. Unknown variants stop after identity and still save an actionable report. Network/HTTP failures produce `REPORT.json` with `status=ERROR`. HTTP redirects, nonlocal hostnames/IPs and replies over 2 MiB are rejected; proxies are disabled. No adapter files are modified.

Offline unit tests are in [tests/test_probe_adapter.py](tests/test_probe_adapter.py) and run through GitHub Actions. These are host simulation tests; **device execution has not yet been independently verified**.

Previous v0.1 release remains [archived](https://github.com/harman-f/harman-ax1800m-adapter-checker/releases/tag/ax1800m-readonly-checker-v0.1). It knows only the older protocol and can wrongly reject a correctly updated October adapter.
