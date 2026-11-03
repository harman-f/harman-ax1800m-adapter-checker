# Recovery and rollback limits — Independent Relay v0.5

`firmware/ax_202610081657_stock_rollback.tar` is the exact October stock application archive (SHA-256 `13ca438ad4db00bbac0fa4650419df110bf17611a69525409261318a8bbade86`, MD5 `fa902131b3c7a11fdd00012b8baceb5a`). It restores the October stock `sdDongle` and its four October companion libraries through the adapter updater protocol.

It does **not** restore the prior March/January application, pairing data, kernel, root filesystem, or complete flash. It is not a full backup and has not been independently validated as physical recovery. Rollback depends on the updater/web endpoint remaining reachable and accepting the October archive.

If a separately authorized bench install is later attempted, keep power connected during upload/install. Treat install as accepted only when the packaged client recognizes the exact updater acknowledgement. The client then requests the documented normal reboot. If acknowledgement or post-reboot reachability is unknown, stop; do not retry, repeatedly reboot, or infer that the runtime binary is active from the version endpoint alone.

A successful rollback acknowledgement is not proof that ordinary CarPlay works. Verify the stock control behavior manually before any further experimental install. v0.5 itself has not been installed or hardware-tested.
