"""Prepare isolated source packages; never overwrite production."""
import hashlib,json,pathlib,re,shutil
P=pathlib.Path(__file__).resolve().parent;ROOT=P.parents[2]
PROD=ROOT/'ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864'
BUILD=P/'build';BUILD.mkdir(exist_ok=True)
variants={'baseline':set(),'baseinv':{'baseinv'},'tobytes':{'tobytes'},'combined':{'baseinv','tobytes'}}
def clean(path):
    return '\n'.join(x.split('//')[0].rstrip() for x in path.read_text().splitlines() if x.split('//')[0].strip())+'\n'
def rename(src,old,new):
    return src.replace('.global '+old,'.global '+new).replace('\n'+old+':','\n'+new+':').replace(old+'_slothy_start',new+'_slothy_start').replace(old+'_slothy_end',new+'_slothy_end')
prefix=(PROD/'gt864_tobytes_public.S').read_text().split('.global C(gt864_tobytes_full_asm)',1)[0]
wrapper=prefix+r'''.global C(gt864_tobytes_full_asm)
C(gt864_tobytes_full_asm):
    mov w5, #0
    b .Lfused_byte_public
.global C(gt864_tobytes_small_asm)
C(gt864_tobytes_small_asm):
    mov w5, #1
.Lfused_byte_public:
    SAVE_PUBLIC
    sub sp, sp, #432
    mov x19, x0
    mov x20, x1
    mov x21, x2
    mov x22, x3
    mov x23, x4
    mov x25, x5
    mov x26, #0
.Lfused_top:
    mov x27, #0
.Lfused_saved_pair:
    mov x9, #864
    madd x10, x26, x9, x20
    mov x11, #0
    mov x9, #16
    cbz x27, .Lfused_offsets
    mov x11, #32
    mov x9, #432
.Lfused_offsets:
    add x1, x10, x11
    add x2, x10, x9
    mov x9, #216
    mov x0, sp
    madd x0, x27, x9, x0
    mov x3, x21
    mov x4, x22
    cbnz x25, .Lfused_saved_small
    bl C(byte_pair_block)
    b .Lfused_saved_done
.Lfused_saved_small:
    bl C(byte_pair_small)
.Lfused_saved_done:
    add x27, x27, #1
    cmp x27, #2
    b.ne .Lfused_saved_pair
    mov x9, #864
    madd x10, x26, x9, x20
    add x1, x10, #448
    add x2, x10, #464
    mov x9, #648
    madd x0, x26, x9, x19
    mov x3, x21
    mov x4, x22
    mov x6, sp
    add x7, sp, #216
    mov x9, x23
    cbnz x25, .Lfused_stream_small
    bl C(pair_merge_full)
    b .Lfused_stream_done
.Lfused_stream_small:
    bl C(pair_merge_small)
.Lfused_stream_done:
    add x26, x26, #1
    cmp x26, #2
    b.ne .Lfused_top
    mov x9, sp
    mov x10, #27
.Lfused_wipe:
    stp xzr, xzr, [x9], #16
    subs x10, x10, #1
    b.ne .Lfused_wipe
    mov x0, x19
    add sp, sp, #432
    RESTORE_PUBLIC
byte_wrapper_end:
'''
audit={}
for name,features in variants.items():
    out=BUILD/name
    if out.exists():shutil.rmtree(out)
    shutil.copytree(PROD,out,ignore=shutil.ignore_patterns('*.o','*.so','PQCkemKAT*','test_kem','PQCgenKAT_kem','check-*'))
    changed=[]
    if 'baseinv' in features:
        for directory,old,new,file in [('baseinv-num-physical','binv_num_fused_tile','binv_num_tile','gt864_native_baseinv_num.S'),
                                       ('baseinv-finish-physical','binv_finish_nocenter_tile','binv_finish_tile','gt864_native_baseinv_finish.S')]:
            (out/file).write_text(rename(clean(P/directory/'candidate.opt.S'),old,new));changed.append(file)
    if 'tobytes' in features:
        (out/'gt864_tobytes_public.S').write_text(wrapper);changed.append('gt864_tobytes_public.S')
        for mode in ['small','full']:
            f=f'gt864_pair_merge_{mode}.S'
            selected=P/f'bytes-{mode}'/'candidate.opt.S'
            assert selected.exists(), 'timing-scheduled ToBytes artifact required'
            (out/f).write_text(clean(selected));changed.append(f)
        vals=json.loads((P/'bytes-small/merge-indices.json').read_text())
        rows=[','.join(map(str,vals[i:i+16]))+',' for i in range(0,len(vals),16)]
        (out/'byte_merge_tables.h').write_text('#include <stdint.h>\nstatic const uint8_t gt864_byte_merge_indices[240] = {\n    '+'\n    '.join(rows)+'\n};\n');changed.append('byte_merge_tables.h')
        make=(out/'Makefile').read_text()
        make=make.replace('gt864_tobytes_merge_core.o','gt864_tobytes_merge_core.o gt864_pair_merge_small.o gt864_pair_merge_full.o',1)
        make=make.replace('gt864_tobytes_small_core.o gt864_tobytes_merge_core.o:',
                          'gt864_tobytes_small_core.o gt864_tobytes_merge_core.o gt864_pair_merge_small.o gt864_pair_merge_full.o:')
        (out/'Makefile').write_text(make);changed.append('Makefile')
    manifest=[]
    for line in (PROD/'SOURCE-MANIFEST.sha256').read_text().splitlines():
        file=line.split('  ',1)[1];manifest.append(hashlib.sha256((out/file).read_bytes()).hexdigest()+'  '+file)
    (out/'SOURCE-MANIFEST.sha256').write_text('\n'.join(manifest)+'\n')
    audit[name]={'changed':sorted(changed),'hashes':{f:hashlib.sha256((out/f).read_bytes()).hexdigest() for f in changed}}
(P/'package-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
print(json.dumps(audit,indent=2))
