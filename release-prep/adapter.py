#!/usr/bin/env python3
"""Local AX1800M/Suding bench uploader. Never run this in car SSH."""
from pathlib import Path
import argparse, hashlib, io, ipaddress, json, re, sys, tarfile, urllib.parse, urllib.request, uuid, zipfile
P=Path(__file__).resolve().parent
UPLOADER_REVISION='ax_independent_uploader_v05'
class Error(Exception):
    def __init__(self,message,install_requested=False):
        super().__init__(message);self.install_requested=install_requested
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs): raise Error('redirect refused')
class Client:
    def __init__(self,host):
        u=urllib.parse.urlsplit('http://'+host)
        try: a=ipaddress.ip_address(u.hostname)
        except (TypeError,ValueError): raise Error('numeric private/local host required')
        if not (a.is_private or a.is_loopback) or u.username or u.password or u.path or u.query or u.fragment: raise Error('invalid local host')
        self.base='http://'+host
        self.opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),NoRedirect())
    def request(self,path,data=None,ctype=None):
        return self.request_raw(path,data,ctype).decode('utf-8','replace')
    def request_raw(self,path,data=None,ctype=None):
        req=urllib.request.Request(self.base+path,data=data)
        if ctype:req.add_header('Content-Type',ctype)
        try:
            with self.opener.open(req,timeout=60) as r:
                data=r.read(16*1024*1024+1)
                if len(data)>16*1024*1024:raise Error('response exceeds 16 MiB')
                return data
        except Exception as e:raise Error(str(e)) from e
def image(kind):
    r=json.loads((P/'IMAGES.json').read_text())[kind];blob=(P/r['file']).read_bytes()
    if hashlib.sha256(blob).hexdigest()!=r['sha256'] or hashlib.md5(blob).hexdigest()!=r['md5']:raise Error('image hash mismatch')
    expected={'sdDongle','libSdAuto.so','libSdCommon.so','libSdSampleRate.so','libSdUtils.so'}
    if kind=='candidate':expected.add('libSdHOct.so')
    with tarfile.open(fileobj=io.BytesIO(blob)) as t:
        m=t.getmembers()
        if len(m)!=len(expected) or {a.name for a in m}!=expected or any(not a.isfile() for a in m):raise Error('unexpected image members')
    return r,blob
def probe(c):
    text=c.request('/cgi-bin/getversion.cgi')
    info={k.strip():v.strip() for line in text.splitlines() if ':' in line for k,v in [line.split(':',1)]}
    if (info.get('platform'),info.get('custom'))!=('AX1800M','suding'):raise Error('unmatched platform/custom; no upload')
    if info.get('system_version')!='202603120956CA':raise Error('unmatched owner system base; no upload')
    if info.get('protocol_version') not in ('20260109175612','20261008165747'):
        # Different system/base variants require explicit inspection, not a broad brand match.
        raise Error('unqualified protocol version '+repr(info.get('protocol_version'))+'; no upload')
    if info.get('product_Model')!='v851se-yunlian-cp':raise Error('unmatched product model; no upload')
    print('IDENTITY='+json.dumps({k:info.get(k) for k in ['platform','custom','system_version','protocol_version','product_Model']},sort_keys=True))
    return info
def has_v05_marker(text):
    return 'AX_INDEPENDENT v=5' in text
def acknowledge(reply, stage, name, final=False, md5=None):
    """Accept known CGI chatter, never infer success from a substring.

    Some vendor CGIs print their Content-Type header inside the HTTP body.
    The first upload also prints temporary-file cleanup and its destination.
    Unknown/error lines or a missing final checksum acknowledgement stop us.
    """
    lines=[s.strip() for s in reply.splitlines() if s.strip()]
    if lines and lines[0].lower()=='content-type: text/html':lines.pop(0)
    if not lines:raise Error(stage+' empty reply')
    terminal=lines.pop()
    # Vendor diagnostics print each digest byte with %x rather than %02x.
    # This ambiguous display is accepted only alongside the exact full digest.
    unpadded=''.join(format(b,'x') for b in bytes.fromhex(md5)) if md5 else None
    full_md5_present=md5 is not None and 'md5_str is '+md5 in lines
    for line in lines:
        cleanup=stage=='upload' and re.fullmatch(r'successfully deleted file: /tmp/[/A-Za-z0-9_.-]+',line)
        destination=stage=='upload' and line=='result is /tmp/'+name
        last_write=stage=='upload' and final and line=='write data------success'
        checksum_context=stage=='upload' and final and md5 is not None and line in ('md5_str is '+md5,md5,'final frame')
        unpadded_context=stage=='upload' and final and full_md5_present and line==unpadded
        extracted=stage=='install' and line in ('sdDongle','libSdH.so','libSdHOct.so','libSdAuto.so','libSdCommon.so','libSdSampleRate.so','libSdUtils.so')
        extraction_command=stage=='install' and re.fullmatch(r'temp is tar -xvf\s+/tmp/'+re.escape(name)+r' -C /usr/data/lib/',line)
        if not (cleanup or destination or last_write or checksum_context or unpadded_context or extracted or extraction_command):raise Error(stage+' unknown/error line: '+repr(line))
    expected={'file check success'} if stage=='upload' and final else {'success','write data------success'} if stage=='upload' else {'success download'}
    if terminal not in expected:raise Error(stage+' rejected/unknown acknowledgement: '+repr(terminal))
    return terminal
def upload(c,r,blob,commit=False):
    probe(c)
    n=(len(blob)+10239)//10240
    for i in range(n):
        name=r['upload_name']+('.0' if i==0 else ':'+r['md5']+'.2' if i==n-1 else '.1')
        boundary=uuid.uuid4().hex
        body=(f'--{boundary}\r\nContent-Disposition: form-data; name="chunk"; filename="{name}"\r\nContent-Type: application/octet-stream\r\n\r\n').encode()+blob[i*10240:(i+1)*10240]+f'\r\n--{boundary}--\r\n'.encode()
        reply=c.request('/cgi-bin/downfile.cgi',body,'multipart/form-data; boundary='+boundary).strip()
        try:acknowledge(reply,'upload',r['upload_name'],final=i==n-1,md5=r['md5'])
        except Error as e:raise Error(f'chunk {i+1}/{n}: {e}; raw_reply={reply!r}') from e
        if i%10==0 or i==n-1:print(f'UPLOAD={i+1}/{n}',flush=True)
    print('ADAPTER_CHECKSUM=PASS')
    if not commit:print('CHECK_ONLY=PASS install_requested=0 upload_cache_changed=1');return
    print('INSTALL=REQUESTING keep_power_connected=1',flush=True)
    reply=None
    try:
        reply=c.request('/cgi-bin/submition.cgi?filename='+urllib.parse.quote(r['upload_name'])+'&').strip()
        acknowledge(reply,'install',r['upload_name'])
    except Error as e:raise Error('install result unknown: '+str(e)+'; raw_reply='+repr(reply),install_requested=True) from e
    print('INSTALL_REPORTED_COMPLETE=1 runtime_verification=PENDING',flush=True)
    try:print('REBOOT_REPLY='+c.request('/cgi-bin/reboot.cgi').strip())
    except Error as e:print('REBOOT_CONNECTION_CLOSED='+str(e))
    print('Wait 30 seconds, reconnect Wi-Fi, then run probe. A version string alone does not verify our hook.')
def main():
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('command',choices=['dry-run','probe','check-only','flash','rollback','logs']);a.add_argument('--host',default='192.168.50.100');a.add_argument('--out',default='logs');args=a.parse_args()
    print('UPLOADER_REVISION='+UPLOADER_REVISION,flush=True)
    if args.command=='dry-run':
        for kind in ['candidate','rollback']:
            r,b=image(kind);print(f'IMAGE={kind} bytes={len(b)} sha256={r["sha256"]}')
        print('DRY_RUN=PASS network_requests=0 device_writes=0');return
    c=Client(args.host)
    if args.command=='probe':probe(c);return
    if args.command=='logs':
        tag='seat-'+uuid.uuid4().hex[:12];dest=Path(args.out);dest.mkdir(parents=True,exist_ok=True)
        (dest/(tag+'-version.txt')).write_text(c.request('/cgi-bin/getversion.cgi'))
        data=c.request_raw('/cgi-bin/minizip.cgi?logID='+tag+'&')
        f=dest/(tag+'.bin');f.write_bytes(data)
        print('LOG_BUNDLE='+str(f.resolve())+' vendor_upload=0 archive_extraction=0')
        if zipfile.is_zipfile(io.BytesIO(data)):
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                for n in z.namelist():
                    if n.endswith('altscreen.log'):
                        entry=z.getinfo(n)
                        if entry.file_size>8*1024*1024:raise Error('oversized altscreen log')
                        text=z.read(n).decode('utf-8','replace');(dest/(tag+'-altscreen.log')).write_text(text)
                        print('RETAINED_BUILD_MARKER='+str(has_v05_marker(text))+' current_process_liveness=UNCONFIRMED')
        return
    kind='rollback' if args.command=='rollback' else 'candidate';r,b=image(kind)
    upload(c,r,b,commit=args.command in ['flash','rollback'])
if __name__=='__main__':
    try:main()
    except (Error,OSError,ValueError,tarfile.TarError) as e:
        print('AX_SEAT=FAIL '+str(e),file=sys.stderr)
        if getattr(e,'install_requested',False):print('INSTALL_REQUESTED=1 result=UNKNOWN retain_power=1 save_output=1',file=sys.stderr)
        else:print('INSTALL_REQUESTED=0 no firmware installation was requested by this invocation',file=sys.stderr)
        print('No retry is automatic.',file=sys.stderr);sys.exit(2)

