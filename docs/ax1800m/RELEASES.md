# Current downloads: firmware candidate and diagnostic

**Only two public releases are maintained.** Both are experimental/pre-release deliverables and serve different purposes. Do not use an old firmware package on the current device.

| Deliverable | Release | Purpose and evidence |
| --- | --- | --- |
| **v0.5 RC2 application test package** | [AX1800M Mini Ultra 1-B v0.5 RC2](https://github.com/harman-f/harman-ax1800m-adapter-checker/releases/tag/ax1800m-miniultra-v0.5-rc2) | Type-111 video and HU→phone presentation-command relay. Host, sanitizer, MIPS cross-build and mocked uploader PASS. **Not installed or vehicle-tested.** |
| **Read-only Adapter Checker v0.2** | [Checker v0.2](https://github.com/harman-f/harman-ax1800m-adapter-checker/releases/tag/ax1800m-readonly-checker-v0.2) | Local GET-only device identity and port diagnostic; Python 3.9/3.12 offline PASS. **Does not approve firmware installation.** |

## Package integrity and installation boundary

- The v0.5 RC2 ZIP SHA-256 is `11ac93b88c65849f8ed3517ca7cbbe0bd93818f881034e9aca8abf853fbc407a`. Its Release also supplies `SHA256SUMS.txt` and `BUILD-SUMMARY.json`.
- The Checker v0.2 Release supplies its own `SHA256SUMS.txt`; verify the downloaded ZIP against that manifest.
- RC2 includes `ax_independent_relay_v05_rc2.tar`, a matching October stock *application* rollback and a guarded Python updater. This is **not** a complete factory flash image or a verified hard-brick recovery method.
- In the RC2 updater, `dry-run` is offline and `probe` is GET-only; `check-only` already uploads temporary chunks, while `flash` and `rollback` modify the device. No installation is authorized based on a version string alone.

## Superseded builds

Previous release candidates, earlier checkers and hardware-specific legacy packages are deliberately **not listed as downloads**. Historical Git tags and commit history may be retained for provenance; they are not firmware compatibility evidence. The old RC1 HU-event interception was incorrect (direct stock call rather than a GOT call); current RC2 is the corrected candidate.

See [stock vs v0.5](STOCK-VS-V05.md), [test matrix](TEST-MATRIX.md), [known issues](KNOWN-ISSUES.md), [compatibility and recovery](COMPATIBILITY-AND-RECOVERY.md). Vendor firmware binaries remain proprietary; the MIT source license does not relicense them.
