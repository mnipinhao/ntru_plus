"""Bind scheduled physical arithmetic to P7-C0, then run native package tests."""
import importlib.util,json,subprocess,sys,shutil
from pathlib import Path
P=Path(__file__).resolve().parent;B=P/'build'
spec=importlib.util.spec_from_file_location('p7c0',P.parent/'inverse-p7c0-range/audit.py')
m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
m.PROD=B/'candidate'
for top in range(2):
    for c in range(16):
        got,_=m.physical_i9(top,c);want=m.i9(m.Model(),top,c,True)
        assert got==want,(top,c)
print('PASS physical P7-C1 arithmetic: 288 terminal maps and ranges',flush=True)
# Existing BaseInv pair symbol lacks its Mach-O alias. Keep this portability
# shim in the Mac-only test snapshot; Linux benchmark sources stay untouched.
macsrc=B/'mac-source'
shutil.copytree(B/'candidate',macsrc,dirs_exist_ok=True)
alias=macsrc/'gt864_native_baseinv_num.S'
alias.write_text('#ifdef __APPLE__\n#define binv_num_pair _binv_num_pair\n#endif\n'+alias.read_text())
subprocess.run([sys.executable,str(P.parent/'verify-production-mac.py'),str(macsrc),str(B/'mac')],check=True)
subprocess.run([sys.executable,str(P.parent/'verify-integrated-components.py'),str(B/'mac'),'--both'],check=True)
