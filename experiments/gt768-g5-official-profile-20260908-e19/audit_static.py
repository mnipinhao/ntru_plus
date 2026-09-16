"""Read-only source arithmetic/inventory checks; no candidate implementation."""
from pathlib import Path
import re,collections,json
R=Path(__file__).resolve().parent
P=Path('/Users/chenpinhao/ntruplus-aarch64-production/ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+768')
O=R/'.build/official'
def ins(s):
    s=re.sub(r'/\*.*?\*/','',s,flags=re.S)
    return [x.strip().split('//')[0].strip() for x in s.splitlines() if re.match(r'^\s*(?:ldr|str|ld1|st1|ldp|stp|mov|movi|sqdmulh|sqrdmulh|srshr|sshr|ushr|shl|mls|and|eor|add|sub|subs|b|bl|ret|trn1|trn2|umov|umax|umaxv|cmhs|cmp|cset)\s',x)]
pack=(P/'pack.S').read_text()
parts={
 'encap_frontend':pack[pack.index('module_pack_.Lwave8_dual_pack_entry:'):pack.index('module_pack_.Lcanonical_pack_compact_core:')],
 'loose_reducer':pack[pack.index('module_pack_.Lcanonical_pack_compact_core:'):pack.index('module_pack_.Lwave8_pack_already_reduced:')],
 'bitpack_core':pack[pack.index('module_pack_.Lwave8_pack_already_reduced:'):pack.index('module_pack_.Lcanonical_pack_compact_q:')],
 'checked_unpack':pack[pack.index('poly_frombytes_encap:'):pack.index('/* END original unpack.S */')]}
d={'inventory':{k:dict(collections.Counter(x.split()[0] for x in ins(v))) for k,v in parts.items()}}
# Exact scalar model of sqrdmulh .8h with positive constant 9; no saturation occurs.
r=[x-3457*((x*9+16384)//32768) for x in range(-32768,32768)]
assert all((y if y>=0 else y+3457)==x%3457 for x,y in zip(range(-32768,32768),r))
d['reciprocal9']={'input':[-32768,32767],'residual':[min(r),max(r)],'canonical_exact_all_65536':True}
def gt(x):return x-3*((((x*21845)//32768)+1)//2)
def off(x):
    y=x-int(x>1728);y+=int(y< -1728)
    return y-3*((y*10923+16384)//32768)
assert all(gt(x)==((x+1)%3)-1 for x in range(-2135,2136))
diff=[x for x in range(-2135,2136) if gt(x)!=off(x)]
d['mod3']={'checked_interval':[-2135,2135],'different_count':len(diff),'examples':{str(x):{'GT':gt(x),'Official':off(x)} for x in [-1729,1728,1729,2135]},'centered_interval_equal':all(gt(x)==off(x) for x in range(-1728,1729))}
# decap_add.S is Official add.s with entry renaming/ELF section plumbing only.
a=(O/'add.s').read_text();b=(P/'decap_add.S').read_text()
b=re.sub(r'#ifdef __APPLE__.*?#endif\n','',b,flags=re.S).replace('poly_sub_decap','poly_sub').replace('gt_decap_poly_triple','poly_triple')
assert ''.join(a.split())==''.join(b.split())
d['decap_add_normalized_identical']=True
(R/'static-audit.json').write_text(json.dumps(d,indent=2)+'\n')
print(json.dumps(d,indent=2))
