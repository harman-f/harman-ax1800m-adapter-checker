#!/usr/bin/env python3
"""Build and run offline checks for the experimental v0.5 relay source only."""
import json
import os
import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent
BUILD = ROOT / "build"
ZIG = pathlib.Path(os.environ.get("ZIG") or shutil.which("zig") or "zig")
HOST_CC = os.environ.get("HOST_CC")
HOST_TARGET = os.environ.get("HOST_TARGET", "x86_64-linux-musl")
HOST_CFLAGS = json.loads(os.environ.get("HOST_CFLAGS_JSON", "[]"))
HOST_RUNNER = json.loads(os.environ.get("HOST_RUNNER_JSON", "[]"))


def run(argv):
    print("+", " ".join(map(str, argv)), flush=True)
    subprocess.run([str(x) for x in argv], check=True, cwd=ROOT)


def wsl_path(path):
    absolute = pathlib.Path(path).resolve()
    drive = absolute.drive.rstrip(":").lower()
    tail = absolute.as_posix().split(":", 1)[1].lstrip("/")
    return f"/mnt/host/{drive}/{tail}"


def main():
    if not ZIG.is_file():
        raise SystemExit(f"pinned Zig compiler not found: {ZIG}")
    version = subprocess.check_output([str(ZIG), "version"], text=True).strip()
    if version != "0.14.1":
        raise SystemExit(f"expected Zig 0.14.1, got {version}")
    BUILD.mkdir(exist_ok=True)
    run([ZIG, "cc", "-target", "mipsel-linux-gnueabihf.2.17", "-mcpu=mips32r2",
         "-shared", "-fPIC", "-Os", "-nostdlib", "-Wl,-soname,libSdHOct.so",
         "-o", BUILD / "libSdHOct.so", ROOT / "src/relay.c", "-lc", "-lpthread"])

    # An explicitly supplied POSIX compiler/flags/runner allow the same tests to
    # run with local Clang or with Zig-built musl binaries launched through WSL.
    host = pathlib.Path(HOST_CC) if HOST_CC else ZIG
    if str(host.resolve()) == str(ZIG.resolve()):
        compiler = [host, "cc", "-target", HOST_TARGET, "-static"]
    else:
        compiler = [host]
    if HOST_RUNNER:
        runner = list(HOST_RUNNER)
    elif os.name == "nt" and HOST_TARGET.endswith("linux-musl"):
        runner = ["wsl.exe", "--distribution", "docker-desktop", "--"]
    else:
        runner = []

    for name in ("relay_test", "geometry_test", "hu_presentation_diag_test"):
        binary = BUILD / name
        run(compiler + ["-std=gnu11", "-Wall", "-Wextra", "-Werror", "-Wno-unused-function",
             "-Wno-unused-variable", "-DMSG_NOSIGNAL=0", "-UNDEBUG", "-O1"] + HOST_CFLAGS +
             [ROOT / f"tests/{name}.c", "-o", binary])
        executable = wsl_path(binary) if runner and runner[0].lower().startswith("wsl") else binary
        run(runner + [executable])
    (BUILD / "BUILD.json").write_text(json.dumps({
        "build": "PASS", "zig": version, "host_target": HOST_TARGET,
        "relay_host_regressions": "PASS", "geometry_regressions": "PASS",
        "hu_presentation_diagnostics": "PASS",
        "device_calls": False, "package_created": False
    }, indent=2) + "\n")


if __name__ == "__main__":
    main()
