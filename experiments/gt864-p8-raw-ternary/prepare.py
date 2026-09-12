"""Frozen P7-C1 package and opt-in P8 package; no production writes."""
from pathlib import Path
import io,tarfile,subprocess,shutil
P=Path(__file__).resolve().parent;R=P.parents[1];B=P/'build'
rel='ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864'
for name in ('baseline','candidate'):
    d=B/name;d.mkdir(parents=True,exist_ok=True)
    data=subprocess.check_output(['git','archive','500f4d59',rel],cwd=R)
    with tarfile.open(fileobj=io.BytesIO(data)) as tar:
        for m in tar.getmembers():
            if m.isfile():
                dst=d/Path(m.name).relative_to(rel);dst.parent.mkdir(parents=True,exist_ok=True)
                dst.write_bytes(tar.extractfile(m).read())
d=B/'candidate'
(d/'gt864_crepmod3_raw.S').write_text((B/'candidate.clean.S').read_text())
p=d/'Makefile';p.write_text(p.read_text().replace('NATIVE_OBJECTS +=','NATIVE_OBJECTS += gt864_crepmod3_raw.o',1))
p=d/'gt864_native_public.S';s=p.read_text()
start=s.index('.p2align 4\n.global C(gt864_inverse_rinv_asm)')
body=s[start:s.rindex('#endif')]
# Keep original centered API. Generate a separate entry with identical control
# and wipe code, not a secret/public selector carried across inner calls.
other=body.replace('gt864_inverse_rinv_asm','gt864_inverse_ternary_asm').replace('.Linv_','.Lp8inv_').replace('C(center864)','C(gt864_crepmod3_raw)').replace('P3-A: one complete normalization pass; constants stay resident.','P8: one raw-to-ternary pass; constants stay resident.')
p.write_text(s[:s.rindex('#endif')]+other+'#endif\n')
p=d/'gt864_native.c';s=p.read_text();f=s[s.index('void gt864_native_inverse(poly'):]
p.write_text(s+'\nvoid gt864_inverse_ternary_asm(int16_t *,const int16_t *,const int16_t *,const int16_t *,const int16_t *,const int16_t *);\n'+f.replace('gt864_native_inverse','gt864_native_inverse_ternary').replace('gt864_inverse_rinv_asm','gt864_inverse_ternary_asm'))
p=d/'gt864_native.h';p.write_text(p.read_text().replace('#endif','/* P8 Decaps consumer: FR0 R^-1 abs<=2497 -> natural ternary. Exact alias. */\nvoid gt864_native_inverse_ternary(poly *out,const poly *in);\n#endif'))
p=d/'kem.c';p.write_text(p.read_text().replace('gt864_native_inverse(&m, &m);\n    poly_crepmod3(&m, &m);','gt864_native_inverse_ternary(&m, &m);'))
# Benchmark the same inverse+conversion boundary, not unlike output APIs.
s=(R/'experiments/gt864-native-asm/inverse-p3b-producer-center/pi-bench.c').read_text()
s=s.replace('static struct api load(','''static invfn old_inverse,old_convert;
static void baseline_ternary(poly *out,const poly *in) {old_inverse(out,in);old_convert(out,out);}
static struct api load(''')
s=s.replace('return (struct api) {','''invfn ternary=(invfn)dlsym(handle,"gt864_native_inverse_ternary");
    if (!ternary) {old_inverse=must(handle,"gt864_native_inverse");old_convert=must(handle,"poly_crepmod3");ternary=baseline_ternary;}
    return (struct api) {''').replace('must(handle, "gt864_native_inverse")','ternary')
(B/'bench.c').write_text(s)
shutil.copyfile(P/'test.c',B/'test.c')
(B/'probe.S').write_text((R/'experiments/gt864-native-asm/integration/probe_inverse.S').read_text().replace('gt864_inverse_rinv_asm','gt864_inverse_ternary_asm'))
shutil.copyfile(R/'experiments/gt864-native-asm/kem-malformed-transcript.c',B/'malformed.c')
