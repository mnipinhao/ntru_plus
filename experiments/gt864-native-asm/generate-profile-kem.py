"""Print KEM-only instrumentation source; arithmetic objects remain unchanged."""
import pathlib,sys
source=pathlib.Path(sys.argv[1]).read_text();gt=sys.argv[2]=='gt'
groups=['Forward','BaseInv','BaseMul_R0','BaseMul_Rinv','BaseMulAdd','Inverse','ToBytes_full','ToBytes_small','FromBytes_checked','CBD','SOTP_encode','SOTP_decode','Triple','Sub','Crepmod3','hash_f','hash_g','hash_h','SHAKE_sampling','RNG','cleanup']
mapping={
 'poly_ntt':('Forward','gt_d1_poly_ntt' if gt else 'poly_ntt',False),
 'poly_baseinv':('BaseInv','gt864_native_poly_baseinv' if gt else 'poly_baseinv',True),
 'poly_basemul':('BaseMul_R0','gt_d1_poly_basemul' if gt else 'poly_basemul',False),
 'poly_basemul_add':('BaseMulAdd','gt_d1_poly_basemul_add' if gt else 'poly_basemul_add',False),
 'poly_cbd1':('CBD','poly_cbd1',False),'poly_sotp_encode':('SOTP_encode','poly_sotp_encode',False),
 'poly_sotp_decode':('SOTP_decode','poly_sotp_decode',True),'poly_triple':('Triple','poly_triple',False),
 'poly_sub':('Sub','poly_sub',False),'poly_crepmod3':('Crepmod3','poly_crepmod3',False),
 'hash_f':('hash_f','hash_f',False),'hash_g':('hash_g','hash_g',False),'hash_h':('hash_h','hash_h',False),
 'shake256':('SHAKE_sampling','shake256',False),'randombytes':('RNG','randombytes',False),'secure_clear':('cleanup','secure_clear',False)}
if gt:
 mapping.update({n:(g,n,ret) for n,g,ret in [('gt864_native_basemul_for_inverse','BaseMul_Rinv',False),('gt864_native_inverse','Inverse',False),('gt864_fr0_tobytes_full','ToBytes_full',False),('gt864_fr0_tobytes_small','ToBytes_small',False),('gt864_fr0_frombytes_checked','FromBytes_checked',True)]})
else:
 mapping.update({n:(g,n,ret) for n,g,ret in [('poly_basemul_scale','BaseMul_Rinv',False),('poly_invntt_scale','Inverse',False),('poly_tobytes','ToBytes_full',False),('poly_frombytes','FromBytes_checked',True)]})
header='\nuint64_t prof_start(void);\nvoid prof_end(int,uint64_t);\n'
# No command-line poly aliases in the profile build. Include the GT API whose
# actual names are called by the generated macros.
if gt:header+='#include "gt864_poly_api.h"\n'
for name,(g,real,ret) in mapping.items():
 body=f'uint64_t _pt=prof_start(); '+(f'int _pr={real}(__VA_ARGS__);' if ret else f'{real}(__VA_ARGS__);')+f' prof_end({groups.index(g)},_pt);'+(' _pr;' if ret else '')
 header+=f'#define {name}(...) '+('({ '+body+' })' if ret else 'do { '+body+' } while(0)')+'\n'
pos=source.index('\n/*************************************************') if gt else source.index('\n#ifdef SUPERCOP')
print(source[:pos]+header+source[pos:])
