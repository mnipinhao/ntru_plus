"""R2: print token-exact symbol mapping patch, preserving all signatures."""
import difflib, hashlib, json, re
from pathlib import Path
R=Path(__file__).resolve().parents[2]
P=R/'ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+768'
mapping={
 'gt_internal_poly_ntt_encap_small':'poly_ntt_encap_small',
 'gt_internal_poly_ntt_loose':'poly_ntt_loose',
 'gt_internal_block_major_poly_ntt_loose':'poly_ntt_loose_block_major',
 'gt_keygen_poly_ntt_to_cq':'poly_ntt_keygen_cq',
 'gt_keygen_baseinv_cq_to_cq_scaled_r':'poly_baseinv_keygen_cq_scaled_r',
 'gt_keygen_basemul_cq_cq_to_cq_scaled_r':'poly_basemul_keygen_cq_scaled_r',
 'gt_keygen_tobytes_cq':'poly_tobytes_keygen_cq',
 'gt_internal_poly_tobytes_from_loose':'poly_tobytes_encap_loose',
 'poly_frombytes':'poly_frombytes_encap',
 'poly_tobytes':'poly_tobytes_encap',
 'poly_basemul_add':'poly_basemul_add_encap',
 'gt_decap_checked_ct_f_basemul_scale64':'poly_frombytes_basemul_decap_scale',
 'gt_decap_poly_frombytes':'poly_frombytes_decap',
 'gt_decap_poly_tobytes':'poly_tobytes_decap',
 'gt_decap_poly_basemul':'poly_basemul_decap',
 'gt_decap_poly_invntt_scale':'poly_invntt_decap_scale',
 'gt_decap_poly_ntt':'poly_ntt_decap',
 'gt_decap_poly_sub':'poly_sub_decap',
}
mapping.update({'_'+k:'_'+v for k,v in list(mapping.items())})
pattern=re.compile(r'(?<![\w.])('+ '|'.join(map(re.escape,sorted(mapping,key=len,reverse=True)))+r')(?![\w.])')
changes={}
for f in P.rglob('*'):
 if f.is_file() and (f.suffix in {'.S','.c','.h','.py','.md'}):
  before=f.read_text(); after=pattern.sub(lambda m:mapping[m[0]],before)
  if before!=after: changes[f]=after
manifest=P/'SOURCE-MANIFEST.sha256'
changes[manifest]=''.join(hashlib.sha256(changes.get(f,f.read_text()).encode()).hexdigest()+'  ./'+str(f.relative_to(P))+'\n' for f in sorted(P.rglob('*')) if f.is_file() and f!=manifest)
print('*** Begin Patch')
for f,after in changes.items():
 print('*** Update File: '+str(f))
 for l in list(difflib.unified_diff(f.read_text().splitlines(),after.splitlines()))[2:]:print('@@' if l.startswith('@@') else l)
print('*** Add File: '+str(Path(__file__).parent/'symbol-map.json'))
for l in json.dumps(mapping,indent=2).splitlines():print('+'+l)
print('*** End Patch')
