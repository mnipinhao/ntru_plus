from pathlib import Path
import shutil,subprocess,sys
P=Path(__file__).resolve().parent;R=P.parents[1];B=P/'build';src=B/'mac-source';out=B/'mac'
shutil.copytree(B/'candidate',src,dirs_exist_ok=True)
p=src/'gt864_native_baseinv_num.S';p.write_text('#ifdef __APPLE__\n#define binv_num_pair _binv_num_pair\n#endif\n'+p.read_text())
subprocess.run([sys.executable,str(R/'experiments/gt864-native-asm/verify-production-mac.py'),str(src),str(out)],check=True)
objects=[str(p) for p in out.glob('*.o')]
subprocess.run(['clang','-O3','-I'+str(src),str(P/'test.c'),str(B/'probe.S'),str(src/'randombytes.c'),*objects,'-o',str(out/'p8-test')],check=True)
subprocess.run([str(out/'p8-test')],check=True)
