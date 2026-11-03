#!/usr/bin/env python3
"""Offline independent relay build. No adapter access."""
from pathlib import Path
import hashlib, io, json, os, re, struct, subprocess, tarfile
P=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
STOCK_SHA='edff2ce4ae238d682fdc45be680d4cab919fc1be09bf398aaff4897289390bcb'
LIBS=['libSdAuto.so','libSdCommon.so','libSdSampleRate.so','libSdUtils.so']
def offset(d,va):
    ph=struct.unpack_from('<I',d,28)[0];num=struct.unpack_from('<H',d,44)[0]
    for i in range(num):
        typ,o,v,_,size,_,_,_=struct.unpack_from('<8I',d,ph+32*i)
        if typ==1 and v<=va<v+size:return o+va-v
    raise ValueError(f'unmapped {va:x}')
def patch(blob):
    assert sha(blob)==STOCK_SHA
    d=bytearray(blob);changes=[]
    # Restore all source inputs to exact stock first; never patch a candidate.
    for va,target in [(0x469950,0x475668),(0x4672c4,0x4660bc),(0x463ddc,0x4726b0),(0x469ca8,0x4726b0),(0x478284,0x4726b0),(0x469a68,0x488180)]:
        o=offset(d,va);word=struct.unpack_from('<I',d,o)[0]
        signed=struct.unpack('<h',struct.pack('<H',word&65535))[0]
        assert word>>16==0x0411 and va+4+signed*4==target,(hex(va),hex(word))
        struct.pack_into('<I',d,o,0x0320f809);changes.append((o,o+4))
    o=offset(d,0x43e424);assert struct.unpack_from('<I',d,o)[0]==0x12000005
    struct.pack_into('<I',d,o,0x10000005);changes.append((o,o+4))
    for va,value in [(0x56526c,0x475668),(0x56518c,0x4660bc),(0x56507c,0x4726b0),(0x565024,0x488180)]:assert struct.unpack_from('<I',d,offset(d,va))[0]==value
    # Add a single absolute dependency inside the existing read-only mapping.
    # Extend both loader and section string-table bounds; no new PT_LOAD/heap shift.
    phoff=struct.unpack_from('<I',d,28)[0];phnum=struct.unpack_from('<H',d,44)[0]
    for i in range(phnum):
        t,o,_,_,size,_,_,_=struct.unpack_from('<8I',d,phoff+32*i)
        if t==2:dynoff,dynsize=o,size
        assert t!=0x6474e552,'RELRO needs a different installation strategy'
    ents=[struct.unpack_from('<iI',d,dynoff+j*8) for j in range(dynsize//8)]
    strva=next(v for t,v in ents if t==5)
    shoff=struct.unpack_from('<I',d,32)[0];shnum=struct.unpack_from('<H',d,48)[0]
    strs=struct.unpack_from('<H',d,50)[0];sbase,ssize=struct.unpack_from('<II',d,shoff+40*strs+16)
    for i in range(shnum):
        h=shoff+40*i;ni=struct.unpack_from('<I',d,h)[0];end=d.index(0,sbase+ni);name=bytes(d[sbase+ni:end])
        if name==b'.rodata':rova,roo,rosize=struct.unpack_from('<III',d,h+12)
        if name==b'.dynstr':strheader=h
        if name==b'.dynsym':symoff,symsize=struct.unpack_from('<II',d,h+16)
    stringoff=offset(d,strva);cache_symbol=False
    for o in range(symoff,symoff+symsize,16):
        ni,value,length,info,other,section=struct.unpack_from('<IIIBBH',d,o)
        end_name=d.index(0,stringoff+ni)
        if bytes(d[stringoff+ni:end_name])==b'gFakeDict':
            assert value==0x566f64 and length==4 and info&15==1
            # gFakeDict is a zero-initialized BSS pointer, not file-backed data.
            headers=[struct.unpack_from('<8I',d,phoff+32*j) for j in range(phnum)]
            assert any(t==1 and flags&2 and va<=value and value+4<=va+memsz
                       for t,_,va,_,_,memsz,flags,_ in headers)
            cache_symbol=True
    assert cache_symbol,'HU /info cache symbol missing'
    dependency=b'/usr/data/lib/libSdHOct.so\0';cave=None
    for o in range(roo+2,roo+rosize-len(dependency)-2):
        if d[o-2:o+len(dependency)+2]==b'\0'*(len(dependency)+4):cave=o;break
    assert cave is not None
    d[cave:cave+len(dependency)]=dependency;changes.append((cave,cave+len(dependency)))
    needed=rova+cave-roo-strva;size=needed+len(dependency)
    end=next(i for i,(t,_) in enumerate(ents) if t==0);assert ents[end+1]==(0,0)
    struct.pack_into('<iI',d,dynoff+8*end,1,needed);changes.append((dynoff+8*end,dynoff+8*end+8))
    si=next(i for i,(t,_) in enumerate(ents) if t==10)
    struct.pack_into('<iI',d,dynoff+8*si,10,size);changes.append((dynoff+8*si,dynoff+8*si+8))
    struct.pack_into('<I',d,strheader+20,size);changes.append((strheader+20,strheader+24))
    assert offset(d,strva+size-1)<len(d)
    diff=[i for i,(a,b) in enumerate(zip(blob,d)) if a!=b]
    assert len(d)==len(blob) and all(any(lo<=i<hi for lo,hi in changes) for i in diff)
    (P/'validation/ELF-PATCH.json').write_text(json.dumps({'stock_sha256':STOCK_SHA,'candidate_sha256':sha(d),'changed_bytes':len(diff),'allowed_ranges':changes,'dynamic_string_bounds_updated':True,'new_load_segments':0,'vehicle_tested':False},indent=2)+'\n')
    return d
def run(args):subprocess.run([str(a) for a in args],check=True)
def main():
    for name in ['build','tmp','validation','firmware']:(P/name).mkdir(exist_ok=True)
    os.environ.update(TMPDIR=str(P/'tmp'),ZIG_LOCAL_CACHE_DIR=str(P/'build/zig-local'),ZIG_GLOBAL_CACHE_DIR=str(P/'build/zig-global'))
    stock=P/'firmware/stock_ax_202610081657.tar';raw=stock.read_bytes()
    assert sha(raw)=='13ca438ad4db00bbac0fa4650419df110bf17611a69525409261318a8bbade86'
    with tarfile.open(stock) as t:
        assert {m.name for m in t.getmembers()}==set(LIBS+['sdDongle'])
        originals={m.name:t.extractfile(m).read() for m in t.getmembers()}
    patched=patch(originals['sdDongle']);(P/'build/sdDongle').write_bytes(patched)
    zig=os.environ['ZIG'];clang=os.environ['CLANG'];sdk=os.environ.get('SDKROOT')
    run([zig,'cc','-target','mipsel-linux-gnueabihf.2.17','-mcpu=mips32r2','-shared','-fPIC','-Os','-nostdlib','-Wl,-soname,libSdHOct.so','-o',P/'build/libSdHOct.so',P/'src/relay.c','-lc','-lpthread'])
    for name in ['relay_test','geometry_test']:
        run([clang]+(['-isysroot',sdk] if sdk else [])+['-std=gnu11','-Wall','-Wextra','-Werror','-Wno-unused-function','-Wno-unused-variable','-DMSG_NOSIGNAL=0','-fsanitize=address,undefined','-O1',P/f'tests/{name}.c','-o',P/f'build/{name}'])
        run([P/f'build/{name}'])
    content={**originals,'sdDongle':patched,'libSdHOct.so':(P/'build/libSdHOct.so').read_bytes()}
    outfile=P/'firmware/ax_independent_v02.tar'
    with tarfile.open(outfile,'w',format=tarfile.GNU_FORMAT) as t:
        for name in LIBS+['sdDongle','libSdHOct.so']:
            data=content[name];m=tarfile.TarInfo(name);m.mode=0o755;m.size=len(data);m.uid=m.gid=m.mtime=0;t.addfile(m,io.BytesIO(data))
    images={}
    for kind,file,upload in [('candidate',outfile,'ax_independent_v02'),('rollback',stock,'ax_202610081657')]:
        b=file.read_bytes();images[kind]={'file':str(file.relative_to(P)),'upload_name':upload,'bytes':len(b),'sha256':sha(b),'md5':hashlib.md5(b).hexdigest()}
    (P/'IMAGES.json').write_text(json.dumps(images,indent=2)+'\n')
    with tarfile.open(outfile) as t:
        for name in LIBS:assert t.extractfile(name).read()==originals[name]
    print(json.dumps({'BUILD':'PASS','images':images,'vehicle_tested':False,'harman_modules_linked':False,'companion_libraries_unchanged':True},indent=2))
if __name__=='__main__':main()
