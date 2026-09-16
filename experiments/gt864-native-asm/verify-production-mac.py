"""Build exact production Makefile source selection on Mac; no timing claims.

Only link mode changes: link the Linux shared-library object list directly into
the existing native test/KAT executables. All build outputs stay in scratch.
"""
import pathlib,subprocess,shlex,sys,hashlib,json
source=pathlib.Path(sys.argv[1]).resolve();out=pathlib.Path(sys.argv[2]).resolve();out.mkdir(parents=True,exist_ok=True)
commands=subprocess.check_output(['make','-Bn','libgt864.so'],cwd=source,text=True).splitlines()
objects=[]
for line in commands:
 cmd=shlex.split(line)
 if '-c' not in cmd:continue
 if '-o' not in cmd:continue
 obj=out/cmd[cmd.index('-o')+1];cmd[cmd.index('-o')+1]=str(obj)
 cmd[0]='clang'
 subprocess.run(cmd,cwd=source,check=True,stdout=subprocess.DEVNULL)
 objects.append(str(obj))
for name,files in [('test_kem',['test/test_kem.c','randombytes.c']),('kat',['kat/PQCgenKAT_kem.c','kat/rng.c','kat/aes.c'])]:
 binary=out/name
 subprocess.run(['clang','-O3','-I.','-Ikat',*files,*objects,'-o',str(binary)],cwd=source,check=True)
 subprocess.run([str(binary)],cwd=out,check=True)
rsp=out/'PQCkemKAT_2624.rsp'
print(json.dumps({'source':str(source),'objects':len(objects),'rsp_sha256':hashlib.sha256(rsp.read_bytes()).hexdigest(),'kat_count':rsp.read_text().count('count = ')}))
