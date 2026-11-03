#!/usr/bin/env python3
"""Reproducible offline AX1800M October v0.5 TEST-ONLY package from pinned public input.
No network, no firmware update, and no hardware operations."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import io
import json
import pathlib
import shutil
import tarfile
import zipfile

HERE=pathlib.Path(__file__).resolve().parent
REPO=HERE.parent
SRC=REPO/"experimental/ax1800m-mini-ultra-october-relay"
STOCK_ZIP=REPO/"AX1800M-Suding-Leon-MU1447-October-v0.2.zip"
PATCH=HERE/"october_stock_patch_v02.py"
PREFIX="AX1800M-Mini-Ultra1B-v0.5-rc2"
ZIP_NAME=PREFIX+".zip"
STOCK_SHA="13ca438ad4db00bbac0fa4650419df110bf17611a69525409261318a8bbade86"
ELF_SHA="edff2ce4ae238d682fdc45be680d4cab919fc1be09bf398aaff4897289390bcb"
PREPARED_SHA="226a99ec2c5a6c62b9d0ae0414ae8b4605c6d158071558015a9a7899566a1ef1"
PATCH_SHA="92d96883599ae8f1eee6a131b52de066c54322646d164cf7206cd7d66c886258"
LIBS=["libSdAuto.so","libSdCommon.so","libSdSampleRate.so","libSdUtils.so"]
STOCK_FILES=LIBS+["sdDongle"]
CANDIDATE_FILES=STOCK_FILES+["libSdHOct.so"]
CANDIDATE_TAR="ax_independent_relay_v05_rc2.tar"
ROLLBACK_TAR="ax_202610081657_stock_rollback.tar"

def sha(data):return hashlib.sha256(data).hexdigest()
def md5(data):return hashlib.md5(data).hexdigest()
def insist(ok,explanation):
    if not ok:raise ValueError(explanation)
def safe_members(data,expected,check_modes=False):
    with tarfile.open(fileobj=io.BytesIO(data),mode="r:") as f:
        ms=f.getmembers()
        insist(len(ms)==len(expected) and {m.name for m in ms}==set(expected),"TAR members mismatch")
        insist(all(m.isfile() and not m.issym() and not pathlib.PurePosixPath(m.name).is_absolute()
          and ".." not in pathlib.PurePosixPath(m.name).parts for m in ms),"unsafe TAR member")
        if check_modes:insist(all(m.mode==0o755 for m in ms),"TAR file mode mismatch")
        return {m.name:f.extractfile(m).read() for m in ms}
def stock_source():
    insist(STOCK_ZIP.is_file(),"legacy public ZIP missing")
    with zipfile.ZipFile(STOCK_ZIP) as z:
        matches=[n for n in z.namelist() if n.endswith("/build-input/stock_ax_202610081657.tar")]
        insist(len(matches)==1,"exact stock input member missing or duplicated")
        stock=z.read(matches[0])
    insist(sha(stock)==STOCK_SHA,"exact October stock TAR SHA-256 mismatch")
    files=safe_members(stock,STOCK_FILES)
    insist(sha(files["sdDongle"])==ELF_SHA,"October sdDongle ELF mismatch")
    return stock,files
def patch_elf(stock_elf,validation_dir):
    insist(sha(PATCH.read_bytes())==PATCH_SHA,"pinned guarded October patch tool changed")
    spec=importlib.util.spec_from_file_location("ax_pinned_patch",PATCH)
    insist(spec and spec.loader,"cannot import pinned patch tool")
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.P=validation_dir.parent
    mod.P.joinpath("validation").mkdir(parents=True,exist_ok=True)
    prepared=bytes(mod.patch(stock_elf))
    insist(sha(prepared)==PREPARED_SHA,"unexpected patched ELF hash")
    insist(len(prepared)==len(stock_elf),"patched binary length changed")
    return prepared
def verify_so(data):
    insist(len(data)>52 and data[:6]==b"\x7fELF\x01\x01","relay library must be ELF32 little-endian")
    insist(int.from_bytes(data[16:18],"little")==3 and int.from_bytes(data[18:20],"little")==8,
           "relay library must be shared EM_MIPS")
    insist(int.from_bytes(data[36:40],"little")==0x70001007,"unexpected MIPS o32 ABI flags")
def make_tar(content):
    buf=io.BytesIO()
    with tarfile.open(fileobj=buf,mode="w",format=tarfile.GNU_FORMAT) as f:
        for n in CANDIDATE_FILES:
            data=content[n];m=tarfile.TarInfo(n)
            m.mode=0o755;m.size=len(data);m.uid=m.gid=m.mtime=0;m.uname=m.gname=""
            f.addfile(m,io.BytesIO(data))
    return buf.getvalue()
def package_zip(path,root,records):
    with zipfile.ZipFile(path,mode="w",compression=zipfile.ZIP_STORED) as z:
        for rel in records:
            info=zipfile.ZipInfo(PREFIX+"/"+rel,date_time=(1980,1,1,0,0,0))
            info.compress_type=zipfile.ZIP_STORED
            info.external_attr=0o100644<<16
            z.writestr(info,(root/rel).read_bytes())
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--so",type=pathlib.Path,required=True)
    ap.add_argument("--out",type=pathlib.Path,required=True)
    ap.add_argument("--source-commit",required=True)
    args=ap.parse_args()
    out=args.out.resolve()
    insist(not out.exists() or not list(out.iterdir()),"output directory must be empty")
    out.mkdir(parents=True,exist_ok=True)
    validation=out/"validation";validation.mkdir()
    dist=out/"dist";dist.mkdir()
    stock_tar,stock_files=stock_source()
    so=args.so.read_bytes();verify_so(so)
    prepared=patch_elf(stock_files["sdDongle"],validation)
    candidate_files=dict(stock_files,sdDongle=prepared)
    candidate_files["libSdHOct.so"]=so
    candidate=make_tar(candidate_files)
    unpacked=safe_members(candidate,CANDIDATE_FILES,True)
    insist(all(unpacked[n]==stock_files[n] for n in LIBS),"stock companion library changed")
    insist(unpacked["sdDongle"]==prepared and unpacked["libSdHOct.so"]==so,"candidate content mismatch")

    bundle=dist/PREFIX;bundle.mkdir()
    fw=bundle/"firmware";fw.mkdir()
    (fw/CANDIDATE_TAR).write_bytes(candidate)
    (fw/ROLLBACK_TAR).write_bytes(stock_tar)
    src_dest=bundle/"source";src_dest.mkdir()
    source_paths=["LICENSE","THIRD_PARTY_NOTICES.md","README.md","build.py",
                  "src/relay.c","src/vendor_abi.h","src/hu_presentation_diag.h",
                  "src/geometry.h","src/seat_profile.h","src/initial_profile.h",
                  "tests/relay_test.c","tests/geometry_test.c","tests/hu_presentation_diag_test.c"]
    for name in source_paths:
        target=src_dest/name;target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(SRC/name,target)

    for name in ["adapter.py","RECOVERY.md"]:
        shutil.copyfile(HERE/name,bundle/name)
    shutil.copyfile(HERE/"START-HERE.md",bundle/"START-HERE.md")
    (bundle/"tests").mkdir()
    shutil.copyfile(HERE/"tests/test_updater.py",bundle/"tests/test_updater.py")

    images={
        "candidate":{"file":"firmware/"+CANDIDATE_TAR,"upload_name":"ax_independent_relay_v05_rc2",
                     "bytes":len(candidate),"sha256":sha(candidate),"md5":md5(candidate)},
        "rollback":{"file":"firmware/"+ROLLBACK_TAR,"upload_name":"ax_202610081657",
                    "bytes":len(stock_tar),"sha256":sha(stock_tar),"md5":md5(stock_tar)}
    }
    (bundle/"IMAGES.json").write_text(json.dumps(images,indent=2)+"\n",encoding="utf8")
    source_hashes={path:sha((SRC/path).read_bytes()) for path in source_paths}
    receipt={"schema":1,"status":"EXPERIMENTAL-OFFLINE-BUILD-NOT-DEVICE-TESTED",
        "source_commit":args.source_commit,"component":"AX1800M Mini Ultra1B",
        "baseline_catalog":"ax_202610081657","pinned_stock_tar_sha256":sha(stock_tar),
        "pinned_stock_sdDongle_sha256":ELF_SHA,
        "prepared_sdDongle_sha256":sha(prepared),
        "library_sha256":sha(so),"candidate_tar_sha256":sha(candidate),
        "source_sha256":source_hashes,
        "guarded_patch_tool_sha256":PATCH_SHA,"device_calls":False,
        "manufacturer_companion_libraries_unchanged":True}
    (bundle/"BUILD-RECEIPT.json").write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf8")
    records=[]
    for f in sorted(bundle.rglob("*")):
        if not f.is_file() or f.name=="MANIFEST.json":continue
        rel=f.relative_to(bundle).as_posix()
        insist(not pathlib.PurePosixPath(rel).is_absolute() and ".." not in pathlib.PurePosixPath(rel).parts,"unsafe ZIP path")
        data=f.read_bytes();records.append({"path":rel,"bytes":len(data),"sha256":sha(data)})
    (bundle/"MANIFEST.json").write_text(json.dumps({
        "schema":1,"status":"TEST-PRERELEASE-NOT-HARDWARE-QUALIFIED",
        "source_commit":args.source_commit,"files":records},indent=2)+"\n",encoding="utf8")
    all_names=["MANIFEST.json"]+[x["path"] for x in records]
    zip_path=dist/ZIP_NAME;package_zip(zip_path,bundle,all_names)
    with zipfile.ZipFile(zip_path) as z:
        insist(z.testzip() is None,"ZIP CRC failure")
        insist(len(z.namelist())==len(all_names),"ZIP member count mismatch")
        for r in records:
            content=z.read(PREFIX+"/"+r["path"])
            insist(sha(content)==r["sha256"],"ZIP record hash mismatch "+r["path"])
    sums=[(zip_path.name,zip_path.read_bytes()),
          (CANDIDATE_TAR,candidate),(ROLLBACK_TAR,stock_tar)]
    (dist/"SHA256SUMS.txt").write_text("".join(sha(data)+"  "+name+"\n" for name,data in sums),encoding="utf8")
    (dist/"BUILD-SUMMARY.json").write_text(json.dumps({
        "package":ZIP_NAME,"zip_bytes":zip_path.stat().st_size,
        "zip_sha256":sha(zip_path.read_bytes()),
        "candidate_sha256":sha(candidate),"candidate_bytes":len(candidate),
        "rollback_sha256":sha(stock_tar),"relay_so_sha256":sha(so),
        "source_commit":args.source_commit,"status":"OFFLINE-PASS-DEVICE-UNTESTED",
        "network_calls":0,"device_writes":0},indent=2)+"\n",encoding="utf8")
    print(json.dumps({"PACKAGE":"PASS","candidate_tar":CANDIDATE_TAR,"candidate_bytes":len(candidate),
                      "candidate_sha256":sha(candidate),"rollback_sha256":sha(stock_tar),
                      "relay_so_sha256":sha(so),"zip":zip_path.name,
                      "zip_sha256":sha(zip_path.read_bytes()),"source_commit":args.source_commit,
                      "device_calls":False},indent=2))
if __name__=="__main__":main()
