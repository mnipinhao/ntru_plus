from pathlib import Path
import hashlib,difflib
p=Path(__file__).resolve().parents[2]/'ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+768'
m=p/'SOURCE-MANIFEST.sha256'
s=''.join(hashlib.sha256(f.read_bytes()).hexdigest()+'  ./'+str(f.relative_to(p))+'\n' for f in sorted(p.rglob('*')) if f.is_file() and f!=m)
print('*** Begin Patch\n*** Update File: '+str(m))
for l in list(difflib.unified_diff(m.read_text().splitlines(),s.splitlines()))[2:]:print('@@' if l.startswith('@@') else l)
print('*** End Patch')
