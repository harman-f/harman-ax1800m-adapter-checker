#!/usr/bin/env python3
"""AX1800M read-only identity and access checker v0.2. Never uploads, installs or logs in."""
import argparse
import ipaddress
import json
from pathlib import Path
import socket
import sys
import urllib.request

VERSION = "0.2"
DEFAULT_HOST = "192.168.50.100"
MAX_RESPONSE = 2 * 1024 * 1024
MODEL = "v851se-yunlian-cp"
SYSTEM = "202603120956CA"
PROTOCOLS = {
    "20260109175612": "pre_october",
    "20261008165747": "october_2026",
}
LOCAL_NETWORKS = tuple(ipaddress.ip_network(net) for net in (
    "10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16", "127.0.0.0/8",
))


class NoRedirect(urllib.request.HTTPRedirectHandler):
    """Refuse redirects; never follow a management page off the local adapter."""

    def redirect_request(self, *args, **kwargs):
        raise ValueError("HTTP redirect refused")


def local_host(value):
    """Accept only explicit local IPv4 addresses, not hostnames or public IPs."""
    address = ipaddress.ip_address(value)
    if address.version != 4 or not any(address in network for network in LOCAL_NETWORKS):
        raise ValueError("Use a private/local IPv4 address (RFC1918 or loopback)")
    return str(address)


def parse_identity(data):
    identity = {}
    for line in data.decode("utf-8", "replace").splitlines():
        if ":" not in line:
            continue
        key, value = (part.strip() for part in line.split(":", 1))
        if key in identity and identity[key] != value:
            raise ValueError("Conflicting identity field: " + key)
        identity[key] = value
    return {key: identity.get(key) for key in (
        "platform", "custom", "product_Model", "system_version", "protocol_version"
    )}


def classify(identity):
    """Known version != firmware flash approval; a reported version cannot prove ELF hashes."""
    core = (identity.get("platform"), identity.get("custom"),
            identity.get("system_version"))
    model = identity.get("product_Model")
    protocol = identity.get("protocol_version")
    if core != ("AX1800M", "suding", SYSTEM) or (model and model != MODEL):
        return {
            "recognized": False,
            "profile": "unknown",
            "reason": "Platform, customization, product model or system differs from studied sample",
        }
    if protocol not in PROTOCOLS:
        return {
            "recognized": False,
            "profile": "unknown",
            "reason": "Unstudied protocol version; no inferred compatibility",
        }
    return {
        "recognized": True,
        "profile": PROTOCOLS[protocol],
        "product_model_evidence": "matched" if model == MODEL else "not_reported",
        "reason": "Version signature recognized for read-only diagnostic only",
    }


def rc2_assessment(classification):
    """Version recognition alone must never be interpreted as an install authorization."""
    if classification["profile"] == "october_2026":
        return {
            "status": "UNVERIFIED_CANDIDATE",
            "install_authorized": False,
            "reason": ("October protocol matches studied sample, but running stock sdDongle ELF "
                       "hash, stock OTA archive, board/ABI and rollback have NOT been verified"),
            "expected_stock_sdDongle_sha256":
                "edff2ce4ae238d682fdc45be680d4cab919fc1be09bf398aaff4897289390bcb",
        }
    if classification["profile"] == "pre_october":
        return {
            "status": "NOT_APPLICABLE_TO_RUNNING_PROTOCOL",
            "install_authorized": False,
            "reason": "RC2 is pinned to the October application, not the pre-October firmware",
        }
    return {
        "status": "UNKNOWN_IDENTITY",
        "install_authorized": False,
        "reason": "No recognized hardware/firmware profile",
    }


def banner(host, port):
    """Connect and read a short unsolicited greeting. Never send credentials or commands."""
    try:
        with socket.create_connection((host, port), timeout=3) as conn:
            conn.settimeout(2)
            try:
                data = conn.recv(512)
            except socket.timeout:
                data = b""
            return {"open": True, "banner": data.decode("ascii", "replace")}
    except OSError as error:
        return {"open": False, "error": str(error)}


def make_opener():
    return urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())


def http_get(opener, host, path):
    request = urllib.request.Request("http://" + host + path, method="GET")
    with opener.open(request, timeout=10) as response:
        if response.status != 200:
            raise ValueError("Unexpected HTTP status for " + path)
        body = response.read(MAX_RESPONSE + 1)
        if len(body) > MAX_RESPONSE:
            raise ValueError("Oversized HTTP reply for " + path)
        return body


def run_probe(host, dest, opener=None, port_check=None):
    """Run read-only scan, always write a structured local report, even on a mismatch."""
    if opener is None:
        opener = make_opener()
    if port_check is None:
        port_check = banner
    report = {
        "checker_version": VERSION,
        "host": host,
        "writes_to_adapter": 0,
        "authentication_attempts": 0,
        "uploads": 0,
        "installs": 0,
        "reboots": 0,
        "status": "ERROR",
        "http": {},
    }
    exit_code = 1
    try:
        version_data = http_get(opener, host, "/cgi-bin/getversion.cgi")
        (dest / "version.txt").write_bytes(version_data)
        report["http"]["/cgi-bin/getversion.cgi"] = {"status": 200, "bytes": len(version_data)}
        identity = parse_identity(version_data)
        report["identity"] = identity
        result = classify(identity)
        report["classification"] = result
        report["rc2_compatibility"] = rc2_assessment(result)
        if not result["recognized"]:
            report["status"] = "UNRECOGNIZED_IDENTITY"
            report["skipped"] = ["web-page", "ssh-banner", "telnet-banner"]
            exit_code = 2
        else:
            web_data = http_get(opener, host, "/")
            (dest / "web-page.html").write_bytes(web_data)
            report["http"]["/"] = {"status": 200, "bytes": len(web_data)}
            for port in (22, 23):
                report[str(port)] = port_check(host, port)
            report["status"] = "COMPLETE"
            exit_code = 0
    except (OSError, ValueError) as error:
        report["error"] = str(error)
        report["status"] = "ERROR"
        exit_code = 1
    finally:
        (dest / "REPORT.json").write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    return report, exit_code


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--out", default="harman-adapter-probe")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    try:
        host = local_host(args.host)
        if args.dry_run:
            print("DRY_RUN=PASS requests=0 writes_to_adapter=0 version=" + VERSION)
            return 0
        dest = Path(args.out)
        dest.mkdir(parents=True, exist_ok=False)
        report, code = run_probe(host, dest)
        print("IDENTITY_STATUS=" + report["status"])
        print("RC2_COMPATIBILITY=" + report.get("rc2_compatibility", {}).get("status", "UNKNOWN"))
        print("REPORT=" + str((dest / "REPORT.json").resolve()))
        print("ADAPTER_WRITES=0 UPLOADS=0 INSTALLS=0 REBOOTS=0")
        return code
    except (OSError, ValueError) as error:
        print("PROBE=FAIL " + str(error) + "; no adapter mutation requested", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
