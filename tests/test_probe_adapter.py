"""Offline tests; never open an actual socket or HTTP connection."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location(
    "axprobe", Path(__file__).resolve().parents[1] / "probe-adapter.py")
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


def version(protocol="20261008165747", model="v851se-yunlian-cp",
            platform="AX1800M", system="202603120956CA"):
    return ("platform: " + platform + "\ncustom: suding\nproduct_Model: " + model
            + "\nsystem_version: " + system + "\nprotocol_version: " + protocol + "\n").encode()


class Response:
    status = 200
    def __init__(self, body):
        self.body = body
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False
    def read(self, count):
        return self.body[:count]


class FakeOpener:
    def __init__(self, body, web=b"<html>read only</html>"):
        self.data = {"/cgi-bin/getversion.cgi": body, "/": web}
        self.methods = []
    def open(self, req, timeout):
        self.methods.append((req.get_method(), req.full_url, timeout))
        path = req.full_url.replace("http://192.168.50.100", "")
        if path not in self.data:
            raise ValueError("Unexpected endpoint")
        return Response(self.data[path])


class CheckerTests(unittest.TestCase):
    def scan(self, body, web=b"<html>read only</html>"):
        with tempfile.TemporaryDirectory() as folder:
            dest = Path(folder)
            opener = FakeOpener(body, web)
            ports = []
            def check(host, port):
                ports.append((host, port))
                return {"open": False}
            report, code = checker.run_probe(
                "192.168.50.100", dest, opener=opener, port_check=check)
            disk_report = json.loads((dest / "REPORT.json").read_text())
            files = sorted(item.name for item in dest.iterdir())
            self.assertEqual(disk_report, report)
            self.assertTrue(all(method == "GET" for method, _, _ in opener.methods))
            self.assertTrue(all(u.startswith("http://192.168.50.100/") for _, u, _ in opener.methods))
            self.assertEqual(report["writes_to_adapter"], 0)
            self.assertEqual(report["authentication_attempts"], 0)
            self.assertEqual(report["uploads"], 0)
            self.assertEqual(report["installs"], 0)
            self.assertEqual(report["reboots"], 0)
            return report, code, files, ports, opener.methods

    def test_post_october_read_only_not_flash_approval(self):
        r, code, files, ports, methods = self.scan(version())
        self.assertEqual(code, 0)
        self.assertEqual(r["classification"]["profile"], "october_2026")
        self.assertEqual(r["rc2_compatibility"]["status"], "UNVERIFIED_CANDIDATE")
        self.assertFalse(r["rc2_compatibility"]["install_authorized"])
        self.assertEqual(len(ports), 2)
        self.assertEqual(len(methods), 2)
        self.assertEqual(files, ["REPORT.json", "version.txt", "web-page.html"])

    def test_pre_october_recognized_not_rc2(self):
        r, code, files, ports, _ = self.scan(version("20260109175612"))
        self.assertEqual(code, 0)
        self.assertEqual(r["classification"]["profile"], "pre_october")
        self.assertEqual(r["rc2_compatibility"]["status"], "NOT_APPLICABLE_TO_RUNNING_PROTOCOL")
        self.assertFalse(r["rc2_compatibility"]["install_authorized"])
        self.assertEqual(len(ports), 2)

    def test_missing_model_is_not_flash_proof(self):
        body = version().replace(b"product_Model: v851se-yunlian-cp\n", b"")
        r, code, _, _, _ = self.scan(body)
        self.assertEqual(code, 0)
        self.assertEqual(r["classification"]["product_model_evidence"], "not_reported")
        self.assertFalse(r["rc2_compatibility"]["install_authorized"])

    def test_unrecognized_firmware_fails_closed_with_report(self):
        r, code, files, ports, methods = self.scan(version("20270801000000"))
        self.assertEqual(code, 2)
        self.assertEqual(r["status"], "UNRECOGNIZED_IDENTITY")
        self.assertEqual(files, ["REPORT.json", "version.txt"])
        self.assertFalse(ports)
        self.assertEqual(len(methods), 1)
        self.assertFalse(r["rc2_compatibility"]["install_authorized"])

    def test_other_model_fails_closed(self):
        r, code, files, ports, _ = self.scan(version(model="other-model"))
        self.assertEqual(code, 2)
        self.assertEqual(files, ["REPORT.json", "version.txt"])
        self.assertFalse(ports)

    def test_other_platform_fails_closed(self):
        r, code, _, ports, _ = self.scan(version(platform="HW301"))
        self.assertEqual(code, 2)
        self.assertFalse(ports)

    def test_other_system_fails_closed(self):
        r, code, _, ports, _ = self.scan(version(system="202504180933CA"))
        self.assertEqual(code, 2)
        self.assertFalse(ports)

    def test_oversized_response_emits_local_error_report(self):
        r, code, files, ports, _ = self.scan(b"a" * (checker.MAX_RESPONSE + 1))
        self.assertEqual(code, 1)
        self.assertEqual(r["status"], "ERROR")
        self.assertIn("Oversized", r["error"])
        self.assertEqual(files, ["REPORT.json"])
        self.assertFalse(ports)

    def test_duplicate_fields_cannot_sneak_through(self):
        r, code, files, ports, _ = self.scan(version() + b"platform: OTHER\n")
        self.assertEqual(code, 1)
        self.assertIn("Conflicting", r["error"])
        self.assertFalse(ports)
        self.assertIn("version.txt", files)

    def test_http_error_reported(self):
        with tempfile.TemporaryDirectory() as folder:
            class ErrorOpener:
                def open(self, request, timeout):
                    raise OSError("offline")
            r, code = checker.run_probe(
                "192.168.50.100", Path(folder), opener=ErrorOpener(),
                port_check=lambda *args: self.fail("network banner must not run"))
            self.assertEqual(code, 1)
            self.assertEqual(r["status"], "ERROR")
            self.assertTrue((Path(folder) / "REPORT.json").is_file())

    def test_only_local_ip_allowed(self):
        for bad in ("google.com", "8.8.8.8", "169.254.1.1", "::1", "224.0.0.1"):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    checker.local_host(bad)
        self.assertEqual(checker.local_host("192.168.50.100"), "192.168.50.100")

    def test_redirect_rejected(self):
        with self.assertRaises(ValueError):
            checker.NoRedirect().redirect_request(None, None, None, None, None, None)

    def test_dry_run_creates_no_files_or_connections(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "not-created"
            result = checker.main(["--host", "192.168.50.100", "--out", str(target), "--dry-run"])
            self.assertEqual(result, 0)
            self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main()
