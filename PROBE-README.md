# Harman's AX1800M/Suding adapter — read-only access check

This is not a firmware fix or an SSH installer. It reads the web identity and page,
then checks whether SSH (22) or Telnet (23) already listens. No login attempt, upload,
updater/recovery command, reboot or configuration change is performed.

1. Power the adapter from the computer/USB supply, separate from the car.
2. Connect the computer's Wi-Fi to the adapter. No internet is needed.
3. Extract this ZIP and open a terminal in its folder.
4. Windows:

```powershell
py probe-adapter.py
```

Mac/Linux:

```sh
python3 probe-adapter.py
```

Default IP is 192.168.50.100. If the adapter's actual management page uses another
local IP, append `--host ACTUAL_IP`. Do not use the car's SSH address.
Allow about 10–30 seconds. Send the resulting `harman-adapter-probe` folder,
containing REPORT.json, version.txt and web-page.html. Files are saved on the computer.
If it fails, send the error; it never falls back to uploading or flashing.

Only target identity accepted: AX1800M/suding, system 202603120956CA,
protocol 20260109175612. A different identity stops further checks.
Python 3.9+ and its standard library are sufficient.

Why this is needed: the public vendor server is currently offering the October
application; direct requests for this adapter's January/March installed versions
did not return firmware. The exact application backup and corresponding rollback
have not been obtained. Olli's previous firmware is not included or relabeled here.

## October OTA and the experimental v0.5 source

The strict checker allowlist above accepts protocol `20260109175612` only. The same Mini Ultra 1-B **after** the October OTA was observed with protocol `20261008165747`. That post-OTA device can be rejected by the checker even when it is functioning correctly; **do not bypass the checker allowlist or infer firmware compatibility from a product label**. The [separate experimental v0.5 source](experimental/ax1800m-mini-ultra-october-relay/README.md) does not change checker behavior, upload or flash anything, or qualify a different system revision.
