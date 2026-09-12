#!/usr/bin/env python3
"""Create frozen P13-A baseline and isolated P13-B package."""
from pathlib import Path
import hashlib,io,shutil,subprocess,tarfile
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];BUILD=HERE/'build'
REV='7073d5ea';PKG='ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864'
archive=subprocess.check_output(['git','archive',REV,PKG],cwd=ROOT)
for label in ('baseline','candidate'):
    d=BUILD/label
    if d.exists():shutil.rmtree(d)
    d.mkdir(parents=True)
    with tarfile.open(fileobj=io.BytesIO(archive)) as tf:
        for m in tf.getmembers():
            if not m.isfile():continue
            target=d/Path(m.name).relative_to(PKG);target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(tf.extractfile(m).read())

c=BUILD/'candidate'
asm=(HERE/'candidate.opt.S').read_text().replace('p13b_i16','lazy_i16')
(c/'gt864_native_inverse16_lazy.S').write_text('/* P13-B Slothy allocated and bounded-window scheduled core. */\n'+asm)
shutil.copyfile(HERE/'composite_tables.h',c/'gt864_p13b_composite_tables.h')
native=c/'gt864_native.c';s=native.read_text()
s=s.replace('#include "gt864_native_scaled_tables.h"','#include "gt864_native_scaled_tables.h"\n#include "gt864_p13b_composite_tables.h"')
old='&gt864_inverse16_main_scale_barrett[0][0][0]'
assert s.count(old)==2
native.write_text(s.replace(old,'&gt864_p13b_main[0][0]'))

manifest=c/'SOURCE-MANIFEST.sha256';known={}
for line in manifest.read_text().splitlines():
    _,name=line.split(None,1);known[name.strip()]=None
known['gt864_p13b_composite_tables.h']=None
manifest.write_text(''.join(f'{hashlib.sha256((c/name).read_bytes()).hexdigest()}  {name}\n' for name in known))

# Reuse the established P13 native/KEM harnesses; only the table argument used
# by the direct AAPCS probe changes for the candidate package.
for name in ('test.c','probe.S','malformed.c','pi-bench.c','run_pi5.py'):
    shutil.copyfile(ROOT/'experiments/gt864-p13-inverse-interior'/name,HERE/name)
test=HERE/'test.c';s=test.read_text().replace('#include "gt864_native_scaled_tables.h"',
 '#include "gt864_native_scaled_tables.h"\n#include "gt864_p13b_composite_tables.h"')
s=s.replace('&gt864_inverse16_main_scale_barrett[0][0][0],','&gt864_p13b_main[0][0],')
test.write_text(s)
print(BUILD)
