"""Create source-only frozen package copies and the existing paired harness."""
from pathlib import Path
import hashlib,json,shutil,subprocess,tarfile,io
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
PROD=ROOT/'ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864'
B=P/'build'
for name in ('baseline','candidate'):
    target=B/name
    if not target.exists():
        # Pin the pre-promotion package, including on a clean checkout after
        # P7-C1 promotion. Do not accidentally benchmark the candidate twice.
        rel=str(PROD.relative_to(ROOT))
        archive=subprocess.check_output(['git','archive','7d2ea7d7',rel],cwd=ROOT)
        target.mkdir(parents=True)
        with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
            for member in tar.getmembers():
                if not member.isfile():continue
                dst=target/Path(member.name).relative_to(rel)
                dst.parent.mkdir(parents=True,exist_ok=True)
                dst.write_bytes(tar.extractfile(member).read())
source='#ifdef __APPLE__\n#define packed_i9 _packed_i9\n#endif\n'+(B/'candidate.clean.S').read_text()
(B/'candidate/gt864_native_inverse9.S').write_text(source)
shutil.copyfile(P.parent/'inverse-p3b-producer-center/pi-bench.c',B/'bench.c')
report={n:hashlib.sha256((B/n/'gt864_native_inverse9.S').read_bytes()).hexdigest() for n in ('baseline','candidate')}
(B/'package-identities.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
