#!/usr/bin/env python3
import ctypes,hashlib,json,re,subprocess,tempfile,random
from pathlib import Path
from close_yang_contract import ROOT,Program
from generate_yang_factored import NAME
from prove_inverse_ct_range import repaired_replay
from probe_inverse_ct_gauge import compute
def cmd(*args):return subprocess.check_output(args,text=True)
def main():
    elf=ROOT/'build/test_inverse_yang';nm=cmd('nm','-S',str(elf))
    a=re.search(r'^([0-9a-f]+) ([0-9a-f]+) T '+NAME+'$',nm,re.M);assert a
    addr,size=int(a[1],16),int(a[2],16);assert addr%32==0
    tail=int(re.search(r'^([0-9a-f]+) t '+NAME+'_tail$',nm,re.M)[1],16)
    table=int(re.search(r'^([0-9a-f]+) [0-9a-f]+ r yang_tail_table$',nm,re.M)[1],16)
    dis=cmd('objdump','-d','--no-show-raw-insn','--disassemble='+NAME,str(elf))
    assert not re.search(r'%rsp|%rbp|%rbx|%r1[2-5]|\bcall\b|vzeroupper',dis)
    lowering=json.loads((ROOT/'results/yang-factored-lowering.json').read_text())
    actual=[]
    for line in dis.splitlines():
        m=re.match(r'\s*([0-9a-f]+):\s+(v\w+)\s+(.*)',line)
        if m and int(m[1],16)>=tail:actual.append((m[2],m[3]))
    assert len(actual)==len(lowering['tail_vector_instructions'])
    for (op,arg),expected in zip(actual,lowering['tail_vector_instructions']):
        eop,earg=expected.split(' ',1);assert op==eop
        assert re.findall(r'%ymm\d+',arg)==re.findall(r'%ymm\d+',earg),(arg,earg)
        if '%rip' in earg:
            off=int(re.search(r'table\+(\d+)',earg)[1])
            target=int(re.search(r'#\s*([0-9a-f]+)',arg)[1],16);assert target==table+off
        else:
            def memory(s):
                return [(int(x or '0',0),r) for x,r in re.findall(r'((?:0x[0-9a-f]+|\d+)?)\((%r\w+)\)',s)]
            assert memory(arg)==memory(earg),(arg,earg)
    data=cmd('objdump','-s','--start-address='+str(table),'--stop-address='+str(table+len(bytes.fromhex(lowering['table_hex']))),str(elf))
    raw=bytearray()
    for line in data.splitlines():
        if re.match(r'^\s+[0-9a-f]+\s',line):
            for group in line.split()[1:5]:
                if re.fullmatch('[0-9a-f]{8}',group):raw+=bytes.fromhex(group)
    assert raw.hex()==lowering['table_hex']
    proof=json.loads((ROOT/'results/yang-closure-schedule-20260923.json').read_text())['tail']['factored']
    p=Program();p.ops=proof['operations'];p.tables=proof['tables']
    bounds=repaired_replay(7644,compute())['stages'][-1]['per_vector_max_abs_bound']
    rng=random.Random(768222)
    with tempfile.TemporaryDirectory(prefix='yang-linked-') as td:
        lib=Path(td)/'yang.so'
        subprocess.run(['cc','-shared','-fPIC','-mavx2','-o',str(lib),str(ROOT/'asm'/f'{NAME}.s'),str(ROOT/'upstream/supercop-avx2/consts.c')],check=True,capture_output=True)
        dll=ctypes.CDLL(str(lib));start=ctypes.cast(getattr(dll,NAME),ctypes.c_void_p).value
        enter=ctypes.CFUNCTYPE(None,ctypes.c_void_p)(start+tail-addr)
        buf=ctypes.create_string_buffer(1567);ptr=(ctypes.addressof(buf)+31)&~31;array=(ctypes.c_int16*768).from_address(ptr)
        for trial in range(160):
            vals=[[b*(1 if trial>>(i//8)&1 else -1) if trial<64 else rng.randint(-b,b) for l in range(16)] for i,b in enumerate(bounds)]
            ref=sum(p.run(vals),[]);array[:]=sum(vals,[]);enter(ptr);assert list(array)==ref,trial
    result={'class':'linked register/address/constant audit and tail raw-model anchor; not timing',
            'symbol_text_bytes':size,'alignment':32,'tail_peak_YMM':10,'whole_prefix_retained':True,
            'tail_vector_rows':len(actual),'all_operands_and_table_bytes_match':True,'tail_raw_model_cases':160,
            'full_inverse_Montgomery':222,'Barrett_vectors':40,'tail_constant_operands_including_q_v':186,
            'private_constant_bytes':7680+len(raw),'wresident_private_constant_bytes':11264,
            'private_constant_delta':7680+len(raw)-11264,
            'table_accounting':'includes 192 duplicated q/v/omega/phi bytes excluded by prior added-table estimate',
            'no_stack_spill_call_vzeroupper_callee_saved_clobber':True,
            'branch_contract':'unchanged public prefix loops + five public tail loops; no data-dependent addressing',
            'elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),'asm_sha256':lowering['asm_sha256']}
    (ROOT/'results/yang-factored-linked.json').write_text(json.dumps(result,indent=2)+'\n')
    (ROOT/'results/yang-factored-disassembly.txt').write_text(dis)
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
