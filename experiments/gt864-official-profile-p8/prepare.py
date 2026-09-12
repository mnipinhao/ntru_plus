from pathlib import Path
import subprocess,io,tarfile
P=Path(__file__).resolve().parent;R=P.parents[1]
rel='ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864'
data=subprocess.check_output(['git','archive','766cc844',rel],cwd=R)
with tarfile.open(fileobj=io.BytesIO(data)) as t:
    for m in t.getmembers():
        if m.isfile():
            p=P/'gt-source'/Path(m.name).relative_to(rel)
            p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(t.extractfile(m).read())
