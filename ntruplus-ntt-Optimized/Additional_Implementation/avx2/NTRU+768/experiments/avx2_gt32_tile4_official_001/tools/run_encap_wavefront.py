#!/usr/bin/env python3
"""Build/audit/verify two bounded wavefronts, then optional short diagnostics.

RDTSCP output is repository-local diagnostic evidence, never SUPERCOP StQ.
"""
import argparse
import collections
import hashlib
import json
import os
import platform
import re
import shutil
import statistics
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLEAN = ROOT.parent.parent/'clean/avx2-gt32-clean'


def run(args, **kwargs):
    try:
        return subprocess.run(list(map(str,args)),check=True,text=True,capture_output=True,**kwargs)
    except subprocess.CalledProcessError as error:
        print(error.stdout or '',file=sys.stderr)
        print(error.stderr or '',file=sys.stderr)
        raise


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser()
    timing=parser.add_mutually_exclusive_group()
    timing.add_argument('--short',action='store_true')
    timing.add_argument('--serious',action='store_true')
    parser.add_argument('--supercop-root',type=Path)
    parser.add_argument('--cpu',type=int,default=1)
    parser.add_argument('--tag',default='encap-range-wavefront-20260921')
    args=parser.parse_args()
    result=ROOT/'results'/args.tag
    if result.exists():
        raise SystemExit(f'refusing overwrite: {result}')
    result.mkdir(parents=True)
    cc=os.environ.get('CC','cc')
    flags=['-O3','-mavx2','-ffunction-sections','-fdata-sections','-Wl,--gc-sections',
           '-Wall','-Wextra','-Werror','-I'+str(CLEAN)]
    backend=[]
    provenance={}
    if args.serious:
        if args.supercop_root is None:
            raise SystemExit('--serious requires --supercop-root; no implicit source update')
        repo=next(p for p in ROOT.parents if (p/'bench/supercop.lock').exists())
        sys.path.insert(0,str(repo/'scripts'))
        from supercop_workflow import read_lock, verify_supercop
        lock=read_lock(repo/'bench/supercop.lock')
        provenance['verified_supercop']=verify_supercop(args.supercop_root,lock)
        provenance['lock']=lock
        libs=list((args.supercop_root/'bench').glob('*/lib/nontimecop/amd64/libcpucycles.a'))
        if len(libs)!=1:raise SystemExit('expected exactly one built SUPERCOP cpucycles backend')
        lib=libs[0];machine=lib.parents[3]
        header=machine/'include/nontimecop/amd64'
        flags += ['-march=native','-mtune=native','-fwrapv','-fPIC','-fPIE','-gdwarf-4',
                  '-DWAVEFRONT_SUPERCOP','-I'+str(header)]
        backend=[lib]
        provenance.update(cpucycles_library_sha256=sha(lib),cpucycles_library=str(lib),
                          cpucycles_header_sha256=sha(header/'cpucycles.h'))
        for path,want in ((f'/sys/devices/system/cpu/cpu{args.cpu}/cpufreq/scaling_governor','performance'),
                          ('/sys/devices/system/cpu/intel_pstate/no_turbo','1')):
            if Path(path).read_text().strip()!=want:raise SystemExit('serious host preflight failed')
    sources=[ROOT/'tests/test_encap_wavefront.c']
    shutil.copy2(sources[0],result/'test_encap_wavefront.measured.c')
    sources += [ROOT/f'generated/encap_wavefront_{n}.s' for n in (1,2)]
    sources += [CLEAN/p for p in ('ntt.s','ntt_m.s','basemul.s','pack.s','cbd.s','consts.c','baseinv.c','add.s')]
    elf=result/'measure'
    cmd=[cc,*flags,*sources,*backend,'-o',elf]
    built=run(cmd);(result/'build.log').write_text(built.stdout+built.stderr)
    validated=run([elf]);(result/'check.out').write_text(validated.stdout+validated.stderr)
    san=result/'check-sanitize'
    sanflags=['-O1','-g','-mavx2','-ffunction-sections','-fdata-sections','-Wl,--gc-sections',
              '-fsanitize=address,undefined','-fno-omit-frame-pointer','-I'+str(CLEAN)]
    run([cc,*sanflags,*sources,'-o',san])
    # LSan cannot attach under the sandbox ptrace restriction. This harness
    # performs no heap allocation; retain ASan/UBSan, disable only leak scanning.
    checked=run([san],env={**os.environ,'ASAN_OPTIONS':'detect_leaks=0'})
    (result/'sanitize.out').write_text(checked.stdout+checked.stderr)
    dis=run(['objdump','-dw',elf]).stdout
    (result/'linked.disasm').write_text(dis)
    search=json.loads((ROOT/'generated/tile4_encap_wavefront_search.json').read_text())
    audits=[]
    for selected in search['selected']:
        name=selected['symbol']
        found=re.search(r'(?m)^([0-9a-f]+) <'+name+r'>:\n(.*?)(?=\n\n)',dis,re.S)
        assert found,name
        address=int(found[1],16)
        instructions=[]
        for line in found[2].splitlines():
            m=re.match(r'\s*[0-9a-f]+:\s+(?:[0-9a-f]{2}\s+)+\s*([a-z][a-z0-9]*)\s*(.*)',line)
            if m: instructions.append((m[1],m[2].split('#')[0].strip()))
        instructions=[p for p in instructions if p[0] not in ('nop','nopl','nopw','cs','data16')]
        assert address%32==0
        assert all(op not in ('call','push','pop') and not op.startswith('j') for op,_ in instructions)
        assert all('%rsp' not in operands and '%rbp' not in operands for _,operands in instructions)
        assert sum(op=='vzeroupper' for op,_ in instructions)==1
        source=(ROOT/('generated/encap_wavefront_'+name[-1]+'.s')).read_text()
        text=source.split(name+':\n')[1].split('.size '+name)[0]
        source_lines=[line.strip() for line in text.splitlines() if line.strip()]
        source_ops=collections.Counter(line.split()[0].replace('movq','mov') for line in source_lines)
        linked_ops=collections.Counter(op for op,_ in instructions)
        assert linked_ops==source_ops,(name,linked_ops-source_ops,source_ops-linked_ops)
        # Preserve the actual ordered machine register flow, not just counts.
        def signature(op,operands):
            return op.replace('movq','mov'),re.findall(r'%(?:ymm|xmm|r)[a-z0-9]+',operands)
        source_flow=[signature(*(line.split(None,1)+[''])[:2]) for line in source_lines]
        linked_flow=[signature(op,operands) for op,operands in instructions]
        assert source_flow==linked_flow,name
        live=set();live_peak=0
        for op,operands in reversed(instructions):
            if op=='vzeroupper':continue
            parts=operands.split(',') if operands else []
            if parts and re.fullmatch(r'%ymm\d+',parts[-1].strip()):
                live.discard(parts[-1].strip())
                parts=parts[:-1]
            live.update(re.findall(r'%ymm\d+',','.join(parts)))
            live_peak=max(live_peak,len(live))
        assert not live,(name,'undefined vector input',live)
        assert live_peak<=16
        loads=sum(op in ('vmovdqu','vmovdqa') and bool(re.match(r'[^,]*\(%r(?:9|dx)\),',operands)) for op,operands in instructions)
        stores=sum(op in ('vmovdqu','vmovdqa') and bool(re.match(r'%ymm\d+,.*\(%r(?:di|dx)\)',operands)) for op,operands in instructions)
        assert loads==selected['data_loads'] and stores==selected['data_stores'],(name,loads,stores)
        audits.append({'symbol':name,'address':hex(address),'address_mod64':address%64,
                       'data_loads':loads,'data_stores':stores,'opcode_histogram':dict(linked_ops),
                       'stack_bytes':0,'calls':0,'branches':0,'internal_vzeroupper':0,
                       'linked_peak_live_ymm':live_peak,
                       'def_use_evidence':'SSA replay, ordered linked/source register-flow equality and backwards machine liveness'})
    host={'cpu':args.cpu,'platform':platform.platform()}
    for key,path in {
        'governor':f'/sys/devices/system/cpu/cpu{args.cpu}/cpufreq/scaling_governor',
        'no_turbo':'/sys/devices/system/cpu/intel_pstate/no_turbo',
        'siblings':f'/sys/devices/system/cpu/cpu{args.cpu}/topology/thread_siblings_list',
        'aslr':'/proc/sys/kernel/randomize_va_space'}.items():
        host[key]=Path(path).read_text().strip() if Path(path).exists() else 'unavailable'
    summary={'label':'repository-local-diagnostic-not-SUPERCOP',
             'elf_sha256':sha(elf),'compiler':run([cc,'--version']).stdout.splitlines()[0],
             'flags':flags,'source_sha256':{str(p.relative_to(ROOT.parent.parent)):sha(p) for p in sources},
             'host':host,'correctness':json.loads(validated.stdout),'audit':audits,
             'sections':run(['size','-A',elf]).stdout,'pricing':[]}
    summary['provenance']=provenance
    summary['sanitizer_policy']='ASan+UBSan; LSan disabled because sandbox disallows ptrace'
    summary['measurement_contract']={
        'modes':['1x_r','1x_m','2x_forward','r_state_plus_hash_input_bytes','polynomial_island'],
        'island':'r/m coefficient inputs + canonical PK bytes -> retained r + r wire bytes + ciphertext; SHAKE excluded',
        'residency':'same immutable r/m/PK banks, same scratch/output banks, 32 alternating warmups',
        'placement':'normal, ASLR-on; not selected from timings'}
    if args.serious:
        summary['label']='supercop-derived-poly'
        pooled=collections.defaultdict(list)
        identities=[]
        for launch in range(9):
            measured=run(['taskset','-c',args.cpu,elf,launch])
            (result/f'serious-{launch}.jsonl').write_text(measured.stdout)
            rows=[json.loads(s) for s in measured.stdout.splitlines()]
            identities.append(next(r for r in rows if 'cpucycles_implementation' in r))
            for mode,v in itertools_product():
                values={who:[r['cycles'] for r in rows if r.get('derived') and r['mode']==mode and r['candidate']==v and r['variant']==who] for who in (0,v)}
                assert all(len(xs)==96 for xs in values.values())
                for who,xs in values.items():pooled[mode,v,who].extend(xs)
                qs={who:quartiles(xs) for who,xs in values.items()}
                summary['pricing'].append({'launch':launch,'mode':mode,'candidate':v,
                                           'stq':qs,'paired_stq2_delta':qs[v][1]-qs[0][1]})
        assert all(x==identities[0] for x in identities)
        summary['identity']=identities[0]
        summary['pooled']=[{'mode':mode,'candidate':v,
                           'control':quartiles(pooled[mode,v,0]),'candidate_stq':quartiles(pooled[mode,v,v]),
                           'delta_stq2':quartiles(pooled[mode,v,v])[1]-quartiles(pooled[mode,v,0])[1],
                           'favorable_launches':sum(r['paired_stq2_delta']<0 for r in summary['pricing'] if r['mode']==mode and r['candidate']==v)} for mode,v in itertools_product()]
        summary['timing_status']='serious-complete'
    if args.short:
        if host['governor']!='performance' or host['no_turbo']!='1':
            summary['timing_status']='blocked-host-preflight'
        else:
            for launch in range(3):
                measured=run(['taskset','-c',args.cpu,elf,'--short'])
                (result/f'short-{launch}.jsonl').write_text(measured.stdout)
                rows=[json.loads(s) for s in measured.stdout.splitlines() if 'diagnostic_rdtscp' in s]
                for mode,candidate in itertools_product():
                    chosen=[r for r in rows if r['mode']==mode and r['candidate']==candidate]
                    medians={v:statistics.median(r['cycles'] for r in chosen if r['variant']==v) for v in (0,candidate)}
                    deltas=[]
                    for b in range(96):
                        by={v:[r['cycles'] for r in chosen if r['block']==b and r['variant']==v] for v in (0,candidate)}
                        deltas.append(statistics.mean(by[candidate])-statistics.mean(by[0]))
                    summary['pricing'].append({'launch':launch,'mode':mode,'candidate':candidate,
                                               'median_cycles':medians,'median_paired_delta':statistics.median(deltas)})
            summary['timing_status']='short-complete'
    (result/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({'result':str(result),'correctness':summary['correctness'],
                      'pricing':summary.get('pooled',summary['pricing'])},indent=2))


def itertools_product():
    return ((mode,v) for mode in range(5) for v in (1,2))


def quartiles(values):
    # Exact stq.h replicated order statistics, not ordinary sample quartiles.
    n=len(values);s=sorted(values*8)
    return [sum(s[n+2*k*n:n+2*(k+1)*n])/(2*n) for k in range(3)]


if __name__=='__main__':
    main()
