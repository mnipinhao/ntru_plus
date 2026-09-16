"""Compare exact deterministic valid and malformed transcripts from two builds."""
import pathlib,subprocess,sys,hashlib,json
p=pathlib.Path(__file__).resolve().parent;prod=p.parents[1]/'ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864'
traces=[]
for arg in sys.argv[1:]:
 b=pathlib.Path(arg).resolve();exe=b/'malformed-transcript'
 subprocess.run(['clang' if sys.platform=='darwin' else 'gcc','-O2','-I'+str(prod),str(p/'kem-malformed-transcript.c'),*map(str,b.glob('*.o')),'-o',str(exe)],check=True)
 traces.append(subprocess.check_output([str(exe)]))
assert len(traces)>=2 and all(x==traces[0] for x in traces)
print(json.dumps({'exact_transcript_equality':'pass','builds':sys.argv[1:],'valid':32,'tampered':32,'malformed':1024,'sha256':hashlib.sha256(traces[0]).hexdigest()}))
