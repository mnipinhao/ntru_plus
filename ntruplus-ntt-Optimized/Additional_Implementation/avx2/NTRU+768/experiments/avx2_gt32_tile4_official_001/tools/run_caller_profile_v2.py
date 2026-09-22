#!/usr/bin/env python3
"""Source-derived cumulative caller profiler; never edits implementation sources.

Each cut gets one counter read inside an otherwise COMPLETE caller execution.
The suffix executes outside the measured interval, preserving output liveness.
No earlier cut is instrumented; no previous cut's warm intermediate is reused.
This is diagnostic source instrumentation, not native measure or cycle-additive
primitive profiling. Full uninstrumented entries expose instrumentation residual.
"""
import argparse
import csv
import io
import json
import os
import re
import shutil
import subprocess
from collections import defaultdict
from pathlib import Path
from run_encap_live_b3_short import EXP, REPO, CLEAN, command, sha, stq, read_lock, verify_supercop

LABELS = {
 'keygen': ['f_retry_loop', 'g_retry_loop', 'first_product', 'PK_pack',
            'second_product_and_f_pack', 'hinv_pack', 'hash_f', 'clear_total', 'external_total'],
 'attempt_f': ['sampling', 'Forward_P', 'BaseInv_J1'],
 'attempt_g': ['sampling', 'Forward_P', 'BaseInv_J1'],
 'encap': ['PK_decode_validate', 'prehash_CBD', 'r_forward', 'r_pack', 'r_hash_g',
           'SOTP', 'm_forward', 'MulAdd', 'CT_pack', 'clear_total', 'external_total'],
 'decap': ['decode_validate', 'BaseMulScale', 'inverse', 'crepmod3',
           'message_forward', 'recovery_product', 'recovered_r_pack',
           'hash_g_SOTP_hash_h', 'reencrypt_forward', 'equality', 'clear_total', 'external_total']}
WINDOWS={
 'encap_ingress':('encap',100,[0],['decode_validate']),
 'decap_ingress':('decap',100,[0],['decode_validate']),
 'encap_dual':('encap',1,[2,3,4],['r_forward','r_forward_pack','r_forward_pack_hash_g']),
 'encap_tail':('encap',6,[7,8],['MulAdd','MulAdd_CT_pack']),
 'encap_m':('encap',5,[6,7,8],['m_forward','m_forward_MulAdd','m_forward_MulAdd_CT_pack']),
 'decap_late':('decap',7,[8,9,10],['reencrypt_forward','reencrypt_equality','reencrypt_equality_clear']),
 'decap_recovery':('decap',3,[4,5,6],['message_forward','message_forward_product','message_forward_product_pack'])}
LABELS.update({k:v[3] for k,v in WINDOWS.items()})

def replace_one(s, old, new):
    assert s.count(old) == 1, (old, s.count(old))
    return s.replace(old, new)

def insert(s, needle, n):
    return replace_one(s, needle, needle + '\nPROFILE_MARK(%d);\n' % n)

def instrument(src, op, gt):
    """Exact source anchors intentionally fail closed when upstream changes."""
    if op.startswith('attempt'):
        if gt:
            src=insert(src, '\t\tscratch->coeff.coeffs[0]++;', 0)
            src=insert(src, '\tforward_p(value, scratch->frontend, scratch->coeff.coeffs);', 1)
        else:
            # Separate anchors for f and g; only selected function is reachable.
            src=insert(src, '    f->coeffs[0] += 1;', 0)
            src=insert(src, '    poly_triple(g);', 0)
            src=insert(src, '    poly_ntt(f);', 1)
            src=insert(src, '    poly_ntt(g);', 1)
        return src
    if op=='keygen':
        if gt:
            anchors=['} while (sample_invertible(&scratch, 1, coins) != 0);',
                     '} while (sample_invertible(&scratch, 0, coins) != 0);',
                     '\t\tscratch->finv);',
                     '\tntruplus768_pack_p_sp1_lazy10788_avx2(pk, scratch->h);',
                     '\t\tscratch->ginv);',
                     '\t\tsk + NTRUPLUS_POLYBYTES, scratch->h);',
                     '\thash_f(sk + 2 * NTRUPLUS_POLYBYTES, pk);',
                     '\tsecure_clear(&scratch, sizeof scratch);']
        else:
            # distinguish the two identical retry loop endings before insertion
            src=replace_one(src,'    } while (r);\n\n    do {','    } while (r);\nPROFILE_MARK(0);\n\n    do {')
            anchors=[None,'    } while (r);\n\n    crypto_kem_keypair_derand',
                     '    poly_basemul(&h, g, finv);','    poly_tobytes(pk, &h);',
                     '    poly_tobytes(sk, f);',
                     '    poly_tobytes(sk + NTRUPLUS_POLYBYTES, &h);',
                     '    hash_f(sk + 2 * NTRUPLUS_POLYBYTES, pk);',
                     '    secure_clear(&ginv, sizeof ginv);']
            src=replace_one(src,anchors[1], '    } while (r);\nPROFILE_MARK(1);\n\n    crypto_kem_keypair_derand')
            anchors[1]=None
    elif op=='encap':
        before='\tif (ntruplus768_unpack_m_avx2' if gt else '    if(poly_frombytes(&h, pk))'
        src=replace_one(src,before,'PROFILE_MARK(100);\n'+before)
        if gt:
            anchors=['\t\treturn 1;\n\t}', '\t\tbuf + NTRUPLUS_SYMBYTES);',
             '\tforward_m(scratch.r, scratch.c, scratch.work);',
             '\tntruplus768_pack_m_lazy10788_avx2(ct, scratch.r);', '\thash_g(ct, ct);',
             '\tpoly_sotp_encode((poly *)(void *)scratch.work, msg, ct);',
             '\tforward_m(scratch.m, scratch.c, scratch.work);',
             '\t\t(const poly *)(const void *)scratch.m);',
             '\tntruplus768_pack_m_highrange12699_avx2(ct, scratch.c);',
             '\tsecure_clear(scratch.m, sizeof scratch.m);']
        else:
            anchors=['        return 1;\n    }', '    poly_cbd1(&r, buf + NTRUPLUS_SYMBYTES);',
             '    poly_ntt(&r);','    poly_tobytes(ct, &r);','    hash_g(ct, ct);',
             '    poly_sotp_encode(&m, msg, ct);','    poly_ntt(&m);',
             '    poly_add(&c, &c, &m);','    poly_tobytes(ct, &c);',
             '    secure_clear(&m, sizeof m);']
    else:
        before='\tint decode_result = ntruplus768_unpack3_m_avx2' if gt else '\tif(poly_frombytes(&c, ct) ||'
        src=replace_one(src,before,'PROFILE_MARK(100);\n'+before)
        if gt:
            anchors=['\t\treturn 1;','\t\tscratch->c, scratch->aux);',
             '\tntruplus768_invntt_tail_avx2(scratch->m, scratch->work);',
             '\tpoly_crepmod3((poly *)(void *)scratch->m);',
             '\tntruplus768_ntt_m_avx2(scratch->work, scratch->aux);',
             '\t\tscratch->c, scratch->hinv);',
             '\tntruplus768_pack_m_centered_avx2(recovered_r, scratch->aux);',
             '\thash_h(hash_h_out, msg);',
             '\tntruplus768_ntt_m_avx2(scratch.hinv, scratch.work);',
             '\t\tscratch.hinv);', '\tsecure_clear(&scratch, sizeof scratch);']
        else:
            anchors=['\t\tgoto cleanup;\n\t}', '\tpoly_basemul_scale(&m, &c, &f);',
             '\tpoly_invntt_scale(&m);','\tpoly_crepmod3(&m);','\tpoly_ntt(&f);',
             '\tpoly_basemul(&f, &c, &hinv);','\tpoly_tobytes(buf1, &f);',
             '\thash_h(buf3, msg);', '\tpoly_ntt(&f);',
             '\tfail |= verify(buf1, buf2, NTRUPLUS_POLYBYTES);',
             '\tsecure_clear(&m, sizeof m);']
            # two Forward calls deliberately have different semantic cutpoints
            assert src.count('\tpoly_ntt(&f);')==2
            src=src.replace('\tpoly_ntt(&f);','\tpoly_ntt(&f);\nPROFILE_MARK(4);',1)
            pos=src.rindex('\tpoly_ntt(&f);')+len('\tpoly_ntt(&f);')
            src=src[:pos]+'\nPROFILE_MARK(8);'+src[pos:]
            anchors[4]=anchors[8]=None
    for n,anchor in enumerate(anchors):
        if anchor: src=insert(src,anchor,n)
    return src

def source_unit(src, op, cut, gt):
    stem=f'{op}_{cut}'
    realop=WINDOWS[op][0] if op in WINDOWS else op
    # Rename exported caller entrypoints; primitives are namespaced at partial link.
    rename={'crypto_kem_keypair':f'kg_{stem}', 'crypto_kem_enc':f'enc_{stem}',
            'crypto_kem_dec':f'dec_{stem}',
            'ntruplus768_keypair_impl':f'kg_{stem}',
            'ntruplus768_enc_derand_impl':f'encd_{stem}',
            'ntruplus768_dec_impl':f'dec_{stem}'}
    pre='#include "caller_profile.h"\n'
    pre+='\n'.join(f'#define {x} {y}' for x,y in rename.items())+'\n'
    # No runtime cutpoint selector, and no bookkeeping before the selected end read.
    endcut=WINDOWS[op][2][cut] if op in WINDOWS else cut
    pre+='#define PROFILE_MARK(n) do { '
    if op in WINDOWS:pre+=f'if ((n)=={WINDOWS[op][1]}) profile_start=cpucycles(); '
    pre+=f'if ((n)=={endcut}) {{ profile_end=cpucycles(); '
    if op=='keygen' and cut==0: pre+='profile_ftries=profile_rng_calls; '
    pre+='} } while(0)\n'
    if op.startswith('attempt'):
        f=op=='attempt_f'
        if gt:
            body=f'keygen_scratch s; int rc=sample_invertible(&s,{int(f)},b->seeds[{"b->ftries-1" if f else "b->totaltries-1"}]); PROFILE_MARK(2); return rc;'
        else:
            body=f'poly x,y; uint8_t tmp[192]; int rc={"genf" if f else "geng"}_derand(&x,&y,tmp,b->seeds[{"b->ftries-1" if f else "b->totaltries-1"}]); PROFILE_MARK(2); return rc;'
    elif realop=='keygen': body=f'return kg_{stem}(b->pk,b->sk);'
    elif realop=='encap': body=f'return {"encd_"+stem if gt else "crypto_kem_enc_derand"}(b->ct,b->ss,b->pk,b->coins);'
    else: body=f'return dec_{stem}(b->ss,b->ct,b->sk);'
    return pre+src+'\n__attribute__((noinline,aligned(32))) int diag_'+stem+'(profile_bank *b) { '+body+' }\n'

def host():
    paths=['/sys/devices/system/cpu/cpu1/cpufreq/scaling_governor',
           '/sys/devices/system/cpu/intel_pstate/no_turbo',
           '/sys/devices/system/cpu/cpu1/topology/thread_siblings_list',
           '/proc/sys/kernel/randomize_va_space']
    h={p:Path(p).read_text().strip() for p in paths}
    assert h[paths[0]]=='performance' and h[paths[1]]=='1' and h[paths[3]]!='0',h
    return h

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--tag',required=True)
    ap.add_argument('--launches',type=int,choices=[0,3,9],default=9)
    ap.add_argument('--sanitize',action='store_true')
    ap.add_argument('--reuse-build',action='store_true')
    ap.add_argument('--aligned-decoder',action='store_true',help='m = aligned decoder, not Mask-store; Encap and Decap')
    a=ap.parse_args()
    if a.launches:
        assert not a.sanitize, 'sanitizer is correctness-only, not timing evidence'
        host()
    assert command(['git','-C',str(REPO),'branch','--show-current']).stdout.strip()=='avx2-gt-ntt'
    sc=Path('/home/nuc/supercop-20260627')
    installed=Path('/home/nuc/src/supercop-maskstore-qualification-20260922/crypto_kem/ntruplus768')
    root=EXP/'results'/a.tag
    root.mkdir(exist_ok=a.reuse_build)
    (root/'.gitignore').write_text('*.o\nmeasure*\n')
    lock=read_lock(REPO/'bench/supercop.lock'); verified=verify_supercop(sc,lock)
    lib,=list((sc/'bench').glob('*/lib/nontimecop/amd64/libcpucycles.a'))
    headers=lib.parents[3]/'include/nontimecop/amd64'
    flags=['-O3','-march=native','-mtune=native','-mavx2','-fwrapv','-fno-strict-aliasing',
           '-fPIE','-ffunction-sections','-fdata-sections','-g',
           '-I'+str(sc/'cryptoint'),'-I'+str(sc/'include')]
    if a.sanitize: flags+=['-O1','-fsanitize=address,undefined','-fno-omit-frame-pointer']
    sources={'o':sc/'crypto_kem/ntruplus768/avx2','g':installed/'avx2-gt32-clean',
             'm':installed/'avx2-gt32-maskstore-exp-sc20260831'}
    if a.aligned_decoder:
        assert not a.reuse_build, 'aligned decoder requires a fresh campaign'
        sources['m']=sources['g']
    manifests={v:{p.name:sha(p) for p in s.iterdir() if p.is_file()} for v,s in sources.items()}
    previous=None
    if a.reuse_build:
        previous=json.loads((root/'metadata.json').read_text())
        assert previous['source_manifests']==manifests
        assert previous['sanitized']==a.sanitize
        assert previous['ELF_sha256']==sha(root/'measure')
        for p in [EXP/'bench/caller_profile.h',EXP/'bench/bench_caller_profile_v2.c']:
            assert previous['support_headers'][str(p)]==sha(p), 'harness changed: build a fresh campaign'
    for p in CLEAN.iterdir():
        if p.is_file() and p.suffix in ('.c','.s','.h') and p.name in manifests['g']:
            original=p.read_text()
            if p.name=='invntt.s': original=original.replace('generated/tile4_inverse_tail_constants.inc','tile4_inverse_tail_constants.inc')
            assert original==(sources['g']/p.name).read_text(),p
    assert sha(CLEAN/'generated/tile4_inverse_tail_constants.inc')==manifests['g']['tile4_inverse_tail_constants.inc']
    commands=list(previous['commands']) if previous else []
    def run(cmd,cwd=None):
        commands.append(list(map(str,cmd)))
        p=subprocess.run(list(map(str,cmd)),cwd=cwd,text=True,capture_output=True)
        with (root/'build.log').open('a') as f:f.write(p.stdout+p.stderr)
        if p.returncode: raise RuntimeError(p.stderr[-6000:])
        return p.stdout
    # Stubs only supply absent SUPERCOP platform declarations, not KEM code.
    (root/'randombytes.h').write_text('void randombytes(unsigned char *, unsigned long long);\n')
    (root/'crypto_kem.h').write_text('/* standalone diagnostic names supplied by generator */\n')
    declarations=[]; table=[]; objects=[]; common=set(); gt_defined=set()
    common_files=['symmetric.c','fips202.c','KeccakP-1600-AVX2.s']
    def normalized(p): return '\n'.join(x.rstrip() for x in p.read_text().splitlines())
    assert all(normalized(sources['o']/n)==normalized(sources['g']/n)==normalized(sources['m']/n) for n in common_files)
    for variant,srcdir in sources.items():
        gt=variant!='o'; partial=root/(variant+'.o'); objs=[]
        names=['poly.c','consts.c','symmetric.c','fips202.c','KeccakP-1600-AVX2.s',
               'cbd.s','crepmod3.s','add.s','ntt.s','invntt.s','basemul.s','pack.s']
        names+=['baseinv.c','ntt_m.s','ntt_p.s','batch_inverse.s'] if gt else ['baseinv.s']
        if gt:names=[n for n in names if n not in common_files]
        if variant=='m':names=[str(EXP/'generated/decode_aligned.S')] if a.aligned_decoder else ['pack.s']
        for n in names:
            obj=root/(variant+'-'+Path(n).name+'.o');objs.append(obj)
            if not a.reuse_build:run(['cc',*flags,'-I'+str(srcdir),'-I'+str(root),'-c',srcdir/n,'-o',obj],srcdir)
            if variant=='o' and n in common_files:
                common.update(l.split()[0] for l in command(['nm','--defined-only','--format=posix',str(obj)]).stdout.splitlines()
                              if len(l.split())>=2 and l.split()[1].isupper())
        for op,labels in LABELS.items():
            realop=WINDOWS[op][0] if op in WINDOWS else op
            if variant=='m' and realop not in (('encap','decap') if a.aligned_decoder else ('encap',)):continue
            file=('keygen' if op.startswith('attempt') else realop)+'.c' if gt else 'kem.c'
            original=(srcdir/file).read_text(); instrumented=instrument(original,realop,gt)
            for cut,label in enumerate(labels):
                # final external-total uses pristine caller text, no internal counter read.
                text=source_unit(original if label=='external_total' else instrumented,op,cut,gt)
                if variant=='m' and a.aligned_decoder:
                    text=('#define ntruplus768_unpack_m_avx2 ntruplus768_exp_aligned_decode\n'
                          '#define ntruplus768_unpack3_m_avx2 ntruplus768_exp_aligned_decode3\n')+text
                unit=root/f'{variant}-{op}-{cut}.c'
                if a.reuse_build:assert unit.read_text()==text, 'generated caller changed: use a new campaign'
                else:unit.write_text(text)
                obj=unit.with_suffix('.o');objs.append(obj)
                if not a.reuse_build:run(['cc',*flags,'-I'+str(EXP/'bench'),'-I'+str(headers),'-I'+str(srcdir),'-I'+str(root),'-c',unit,'-o',obj],srcdir)
                symbol=f'{variant}_diag_{op}_{cut}'
                declarations.append(f'int {symbol}(profile_bank *);')
                table.append((op,cut,label,variant,symbol))
        if not a.reuse_build:
            run(['ld','-r',*objs,'-o',partial])
            nm=run(['nm','--defined-only','--format=posix',partial])
            names=[l.split()[0] for l in nm.splitlines() if len(l.split())>=2 and l.split()[1].isupper()]
            if variant=='g':gt_defined=set(names)
            mapping=root/(variant+'-symbols.map')
            undefined={l.split()[0] for l in run(['nm','--undefined-only','--format=posix',partial]).splitlines()}
            remap={n:f'{variant}_{n}' for n in names}
            remap.update({n:'o_'+n for n in undefined & common})
            if variant=='m':remap.update({n:'g_'+n for n in undefined & gt_defined})
            mapping.write_text(''.join(f'{n} {v}\n' for n,v in sorted(remap.items())))
            run(['objcopy','--redefine-syms='+str(mapping),partial])
        objects.append(partial)
    (root/'entries.h').write_text('\n'.join(declarations)+'\nstatic entry entries[]={\n'+
        ''.join(f'{{"{op}",{cut},"{label}",\'{variant}\',{symbol}}},\n' for op,cut,label,variant,symbol in table)+'};\n')
    elf=root/'measure'
    if not a.reuse_build or not elf.exists():
        run(['cc',*flags,'-I'+str(root),'-I'+str(EXP/'bench'),'-I'+str(headers),
             EXP/'bench/bench_caller_profile_v2.c',*objects,lib,lib.parents[2]/'amd64/libsupercop.a','-Wl,--gc-sections','-o',elf])
    (root/'symbols.txt').write_text(command(['nm','-n','-S',str(elf)]).stdout)
    (root/'sections.txt').write_text(command(['readelf','-SW',str(elf)]).stdout)
    if a.aligned_decoder:
        run(['python3',EXP/'tools/audit_decode_aligned.py',elf,root])
    env={**os.environ,'ASAN_OPTIONS':'detect_leaks=0'}
    pre=subprocess.run([str(elf),'check'],env=env,text=True,capture_output=True)
    (root/'preflight.out').write_text(pre.stdout);(root/'preflight.err').write_text(pre.stderr)
    assert pre.returncode==0,pre.stderr[-4000:]
    metadata={'label':'supercop-derived-poly caller profiler; not Native', 'lock':lock,'verified':verified,
      'source_manifests':manifests,'ELF_sha256':sha(elf),'counter_library_sha256':sha(lib),
      'stq_header_sha256':sha(sc/'include/stq.h'),'commands':commands,'compiler':command(['cc','--version']).stdout,
      'residency':'8 deterministic banks; same mutable physical slot for all variants; full reset and one full warmup outside timing',
      'cutpoint_policy':'one internal end read; complete suffix untimed and checked; independent full restart for each cut; external_total no internal read',
      'keygen_rng':'same precomputed 64x32-byte coin stream, memcpy randombytes; excludes system entropy generation, includes retries',
      'attempt_domain':'last successful f/g coin in each actual retry trace; not the retry-inclusive headline',
      'placement':'normal / ASLR on, fixed before timing','launches':a.launches,'sanitized':a.sanitize,
      'topology':command(['lscpu','-J']).stdout}
    metadata['support_headers']={str(p):sha(p) for p in [sc/'cryptoint/crypto_uint64.h',
        sc/'cryptoint/crypto_int16.h',sc/'cryptoint/crypto_uint32.h',sc/'include/crypto_declassify.h',
        EXP/'bench/caller_profile.h',EXP/'bench/bench_caller_profile_v2.c',Path(__file__)]}
    metadata['retry_coverage']='all sampled attempts preserved; natural retry observations reported in preflight; zero observed does not establish failed-retry coverage'
    metadata['counter_reports']=[]
    metadata['variant_roles']={'o':'Official','g':'Current GT','m':'aligned decoder' if a.aligned_decoder else 'Mask-store'}
    if a.aligned_decoder:
        metadata['aligned_decoder_sources']={str(p):sha(p) for p in [EXP/'generated/decode_aligned.S',EXP/'generated/decode_aligned_lowering.json',EXP/'tools/generate_decode_aligned.py',EXP/'tools/audit_decode_aligned.py']}
    metadata['shared_helpers']={'trailing_whitespace_normalized_identical_sources':common_files,
        'policy':'one hash/SHAKE/Keccak body; m reuses Current primitives except '+('decode' if a.aligned_decoder else 'pack')+'; diagnostic image, not Native placement'}
    metadata['nested_windows']=WINDOWS
    metadata['window_policy']='entire caller still starts from identical reset; real prefix runs untimed; one start and one end read inside selected region; never uses synthetic preprojected state'
    groups=defaultdict(list);launchgroups=defaultdict(list)
    for launch in range(a.launches):
        metadata.setdefault('host_checks',[]).append(host())
        proc=subprocess.run(['taskset','-c','1',str(elf)],text=True,capture_output=True,env=env)
        (root/f'launch-{launch}.csv').write_text(proc.stdout);(root/f'launch-{launch}.err').write_text(proc.stderr)
        assert proc.returncode==0,proc.stderr
        assert 'cpucycles_implementation=default-perfevent ' in proc.stderr, 'counter backend changed'
        metadata['counter_reports'].append(proc.stderr)
        for row in csv.DictReader(io.StringIO(proc.stdout)):
            k=(row['op'],int(row['cut']),row['variant'])
            groups[k].append(int(row['cycles']));launchgroups[(launch,*k)].append(int(row['cycles']))
    result={};waterfall=[]
    for op,labels in LABELS.items():
        result[op]={}
        for cut,label in enumerate(labels):
            vals={v:stq(groups[op,cut,v]) for v in sources if (op,cut,v) in groups}
            if not vals:continue
            deltas={v:[stq(launchgroups[k,op,cut,v])[1]-stq(launchgroups[k,op,cut,'o'])[1]
                       for k in range(a.launches)] for v in vals if v!='o'}
            result[op][label]={'StQ':vals,'launch_delta_vs_official':deltas}
            if 'm' in vals:result[op][label]['launch_candidate_minus_current' if a.aligned_decoder else 'launch_mask_minus_current']=[stq(launchgroups[k,op,cut,'m'])[1]-stq(launchgroups[k,op,cut,'g'])[1] for k in range(a.launches)]
            # Telescoping one estimator: pooled cumulative StQ2, never median of independently differenced components.
            for v in vals:
                prev=stq(groups[op,cut-1,v])[1] if cut else 0
                waterfall.append({'op':op,'cut':cut,'label':label,'variant':v,'cumulative_StQ2':vals[v][1],
                                  'increment_StQ2':vals[v][1]-prev})
    (root/'metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')
    for v,s in sources.items():
        archived=root/'installed-sources'/v;archived.mkdir(parents=True,exist_ok=True)
        for p in s.iterdir():
            if p.is_file():shutil.copyfile(p,archived/p.name)
    archived=root/'harness-sources';archived.mkdir(exist_ok=True)
    for p in [Path(__file__),EXP/'bench/caller_profile.h',EXP/'bench/bench_caller_profile_v2.c']:
        shutil.copyfile(p,archived/p.name)
    if a.aligned_decoder:
        for path in metadata['aligned_decoder_sources']:
            p=Path(path);shutil.copyfile(p,archived/p.name)
    (root/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
    if waterfall:
        with (root/'waterfall.csv').open('w') as f:
            w=csv.DictWriter(f,fieldnames=list(waterfall[0]));w.writeheader();w.writerows(waterfall)
    assert manifests=={v:{p.name:sha(p) for p in s.iterdir() if p.is_file()} for v,s in sources.items()}
    print(root)

if __name__=='__main__':main()
