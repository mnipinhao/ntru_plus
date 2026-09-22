#!/usr/bin/env python3
"""Fixed, equally caged C/I/M comparison. No Native or promotion."""
import argparse
import csv
import io
import json
import os
import re
import platform
from collections import defaultdict
from pathlib import Path
from run_encap_live_b3_short import REPO,EXP,CLEAN,stq,command,sha,read_lock,verify_supercop
from generate_pack_triad import build as generate
from vector_mapping_source_ledger import stats

def audit(elf,root,selected=None):
    _,model=generate()
    # Assemble expected paths independently in an object for exact operands,
    # then resolve every linked memory constant to its actual bytes.
    report={}
    nm=command(['nm','-S',str(elf)]).stdout
    image=elf.read_bytes();sections=[]
    for line in command(['objdump','-h',str(elf)]).stdout.splitlines():
        w=line.split()
        if len(w)>=7 and w[0].isdigit():sections.append((int(w[3],16),int(w[2],16),int(w[5],16)))
    def read32(addr):
        for v,size,off in sections:
            if v<=addr and addr+32<=v+size:return image[off+addr-v:off+addr-v+32]
        raise AssertionError(addr)
    def normalize(x):
        x=re.sub(r'(\d+)\+(\d+)\(',lambda m:str(int(m[1])+int(m[2]))+'(',x)
        x=re.sub(r'-?0x[0-9a-f]+\(%rip\)','CONST(%rip)',x)
        x=re.sub(r'\.L\w+\(%rip\)','CONST(%rip)',x)
        x=re.sub(r'\$0x([0-9a-f]+)',lambda m:'$'+str(int(m[1],16)),x)
        x=re.sub(r'0x([0-9a-f]+)\(',lambda m:str(int(m[1],16))+'(',x)
        x=x.replace('(%rsi)','0(%rsi)') if re.search(r'(?<![0-9])\(%rsi\)',x) else x
        x=re.sub(r'(?<![0-9])\(%rdi\)','0(%rdi)',x)
        return re.sub(r'\s+','',x)
    addresses=[]
    for key in (selected or dict.fromkeys('cim')):
        name=selected[key] if selected else 'ntruplus768_exp001_pack_triad_'+key
        m=re.search(r'^([0-9a-f]+) ([0-9a-f]+) T '+name+'$',nm,re.M);assert m
        address,size=int(m[1],16),int(m[2],16);assert address%32==0 and size==5120
        addresses.append(address)
        raw=command(['objdump','-d','--no-show-raw-insn','--disassemble='+name,str(elf)]).stdout
        (root/(key+'.disassembly.txt')).write_text(raw)
        ins=[];constants=[]
        for line in raw.splitlines():
            z=re.match(r'\s*[0-9a-f]+:\s+(.+)',line)
            if not z:continue
            x=z[1].split('#')[0].strip();ins.append(x)
            if '(%rip)' in x:
                addr=int(re.search(r'#\s*([0-9a-f]+)',z[1])[1],16)
                assert addr%32==0
                constants.append(read32(addr))
            if x=='ret':break
        expected=model['paths'][key]
        actual_norm=[normalize(x) for x in ins]; expected_norm=[normalize(x) for x in expected]
        assert actual_norm==expected_norm,(key,len(ins),len(expected),
            [(x,y) for x,y in zip(actual_norm,expected_norm) if x!=y][:4])
        expected_constants=[]
        for x in expected:
            m=re.search(r'(\.L\w+)\(%rip\)',x)
            if m:
                values,width=model['constants'][m[1]]
                expected_constants.append(b''.join(v.to_bytes(width,'little') for v in values))
        assert constants==expected_constants
        assert not any(re.search(r'%(rsp|rbp|rbx|r1[2-5])\b',x) or x.startswith(('call','push','pop','j')) for x in ins)
        assert ins.count('vzeroupper')==expected.count('vzeroupper')==1
        ledger=stats(ins);assert ledger['peak_live_YMM']<=16
        ledger['evidence']='linked instruction def/use replay; VEX XMM writes kill upper YMM'
        hot_end=int(re.search(r'^\s*([0-9a-f]+):\s+ret\b',raw,re.M)[1],16)+1
        report[key]={'address':address,'size':size,'hot_bytes':hot_end-address,
                     'ledger':ledger,'vzeroupper':'one inherited, unchanged',
                     'constant_bytes':[x.hex() for x in constants],
                     'proof':'exact linked operands and memory constants match executable model; no stack/calls/branches'}
        highname='ntruplus768_pack_m_highrange12699_avx2' if selected else name+'_highrange'
        high=command(['objdump','-d','--no-show-raw-insn','--disassemble='+highname,str(elf)]).stdout
        assert re.search(r'jmp\s+[0-9a-f]+ <'+name+'>',high)
        report[key]['highrange_disassembly']=high
    if not selected:assert addresses[1]-addresses[0]==addresses[2]-addresses[1]==5120
    return report

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--supercop-root',type=Path,required=True)
    ap.add_argument('--tag',required=True)
    ap.add_argument('--launches',type=int,choices=(3,9),default=3)
    a=ap.parse_args()
    assert command(['git','branch','--show-current']).stdout.strip()=='avx2-gt-ntt'
    host={x:Path(x).read_text().strip() for x in [
        '/sys/devices/system/cpu/cpu1/cpufreq/scaling_governor','/sys/devices/system/cpu/intel_pstate/no_turbo',
        '/sys/devices/system/cpu/cpu1/topology/thread_siblings_list','/proc/sys/kernel/randomize_va_space']}
    assert list(host.values())[0]=='performance' and list(host.values())[1]=='1' and list(host.values())[3]!='0'
    lock=read_lock(REPO/'bench/supercop.lock');verified=verify_supercop(a.supercop_root,lock)
    root=EXP/'results'/a.tag;root.mkdir(exist_ok=False)
    (root/'.gitignore').write_text('*.o\nmeasure\n')
    checked=command(['make','pack-maskstore-check'])
    (root/'correctness.log').write_text(checked.stdout+checked.stderr)
    modelcheck=command(['python3','tools/research_pack_mask_network.py','--check'])
    (root/'model-check.log').write_text(modelcheck.stdout+modelcheck.stderr)
    lib,=list((a.supercop_root/'bench').glob('*/lib/nontimecop/amd64/libcpucycles.a'))
    headers=lib.parents[3]/'include/nontimecop/amd64'
    cc=os.environ.get('CC','cc');flags=['-O3','-march=native','-mtune=native','-mavx2','-fwrapv','-fno-strict-aliasing','-fPIE','-ffunction-sections','-fdata-sections']
    commands=[];sources=[];objects=[]
    official=a.supercop_root/'crypto_kem/ntruplus768/avx2'
    for name in ['ntt.s','basemul.s','pack.s','consts.c']:
        src=official/name;obj=root/(name+'.o')
        cmd=[cc,*flags,'-I'+str(official),'-c',str(src),'-o',str(obj)]
        commands.append(cmd);command(cmd)
        cmd=['objcopy','--prefix-symbols=official_',str(obj)];commands.append(cmd);command(cmd)
        sources.append(src);objects.append(obj)
    local=[EXP/'bench/bench_pack_triad.c',EXP/'generated/pack_triad.S']+[CLEAN/x for x in [
        'baseinv.c','consts.c','poly.c','symmetric.c','fips202.c','KeccakP-1600-AVX2.s',
        'cbd.s','crepmod3.s','add.s','ntt.s','ntt_m.s','basemul.s','batch_inverse.s','pack.s']]
    sources+=local;elf=root/'measure'
    cmd=[cc,*flags,'-Wl,--gc-sections','-I'+str(CLEAN),'-I'+str(headers),*map(str,local),*map(str,objects),str(lib),'-o',str(elf)]
    commands.append(cmd);built=command(cmd);(root/'build.log').write_text(built.stdout+built.stderr)
    linked=audit(elf,root);(root/'linked-audit.json').write_text(json.dumps(linked,indent=2)+'\n')
    (root/'symbols.txt').write_text(command(['nm','-n','-S',str(elf)]).stdout)
    (root/'sections.txt').write_text(command(['readelf','-SW',str(elf)]).stdout)
    command([str(elf),'--check'])
    sources += list(EXP.glob('tools/*pack*triad*.py'))+[EXP/'tools/research_pack_mask_network.py',EXP/'bench/bench_encap_fn.c']
    sources += list(EXP.glob('tests/test_pack*store*.c'))+[EXP/'tests/test_pack_identity14.c',EXP/'tests/test_encap_live_b3_pack_kem.c',EXP/'src/encap_pack_maskstore_research.c']
    sources += list(CLEAN.glob('*.h'))
    sources += [EXP/'tools/run_encap_live_b3_short.py',EXP/'tools/vector_mapping_source_ledger.py',
                EXP/'tools/generate_pack_identity14.py',EXP/'tools/generate_tile4.py',
                EXP/'generated/pack_identity14_mapping.h',EXP/'Makefile',REPO/'bench/supercop.lock']
    manifest={str(p):sha(p) for p in sources}
    snap=root/'source-snapshot';snap.mkdir()
    for p in sources:
        target=snap/sha(p)
        if not target.exists():target.write_bytes(p.read_bytes())
    metadata={'label':'supercop-derived-poly; NOT Native',
        'tier':'serious' if a.launches==9 else 'diagnostic','host':host,'lock':lock,'verified':verified,
        'compiler':command([cc,'--version']).stdout,'commands':commands,'source_sha256':manifest,
        'clean_manifest':{str(p.relative_to(CLEAN)):sha(p) for p in sorted(CLEAN.rglob('*')) if p.is_file()},
        'elf_sha256':sha(elf),'cpucycles_library_sha256':sha(lib),'stq_sha256':sha(a.supercop_root/'include/stq.h'),
        'platform':platform.platform(),'topology':command(['lscpu','-J']).stdout,
        'setting':'normal / ASLR-on; preselected','residency':'same addresses; 8 banks; reset and matching warmup outside timing',
        'order':'ABC BCA CAB CBA BAC ACB repeated 16 times; 96 observations/variant/region/launch',
        'eager':'not integrated','prefixed_hash':'not integrated','fresh_processes':a.launches}
    values=defaultdict(list);launches=defaultdict(list);backends=[]
    host_checks=[]
    for k in range(a.launches):
        before={p:Path(p).read_text().strip() for p in host}
        assert before==host,'host controls changed; stop timing'
        proc=command(['taskset','-c','1',str(elf)])
        after={p:Path(p).read_text().strip() for p in host}
        assert after==host,'host controls changed during launch'
        host_checks.append({'before':before,'after':after})
        (root/f'launch-{k}.csv').write_text(proc.stdout);(root/f'launch-{k}.err').write_text(proc.stderr)
        assert 'preflight=pass' in proc.stderr;backends.append(proc.stderr)
        for row in csv.DictReader(io.StringIO(proc.stdout)):
            r,v,c=(int(row[x]) for x in ('region','variant','cycles'))
            values[r,v].append(c);launches[k,r,v].append(c)
        assert all(len(launches[k,r,v])==96 for r in range(4) for v in range(3))
    metadata['counter_backend']=backends
    metadata['host_checks']=host_checks
    assert len({re.search(r'cpucycles=(\S+) cpucycles_persecond=(\d+)',x).groups() for x in backends})==1
    assert metadata['clean_manifest']=={str(p.relative_to(CLEAN)):sha(p) for p in sorted(CLEAN.rglob('*')) if p.is_file()}
    assert all(sha(Path(p))==h for p,h in manifest.items()),'source changed during campaign'
    assert sha(elf)==metadata['elf_sha256']
    summary={}
    for r,name in enumerate(['r_pack','c_pack','r_state_hashbytes','full_polynomial_island']):
        qs={v:stq(values[r,v]) for v in range(3)}
        result={'stq':qs,'deltas':{}}
        for label,left,right in [('I-C',1,0),('M-I',2,1),('M-C',2,0)]:
            delta=[stq(launches[k,r,left])[1]-stq(launches[k,r,right])[1] for k in range(a.launches)]
            result['deltas'][label]={'pooled_StQ2':qs[left][1]-qs[right][1],'launches':delta,'favorable':sum(x<0 for x in delta)}
        summary[name]=result
    (root/'metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')
    (root/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
