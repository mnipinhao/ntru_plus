#!/usr/bin/env python3
"""Archive source and verify installed linked serializer and Native observations."""
import json
import shutil
import sys
from pathlib import Path
from install_pack_maskstore import EXP,REPO,CLEAN,sha
from run_pack_triad import audit
sys.path.insert(0,str(REPO/'scripts'))
from run_supercop_benchmark import elf_layout,decode_observations,stabilized_quartiles

if __name__=='__main__':
    root=EXP/'results/maskstore-native-qualification-20260922'
    serious=json.loads((EXP/'results/pack-maskstore-triad-serious-20260922/metadata.json').read_text())
    assert all(sha(CLEAN/p)==h for p,h in serious['clean_manifest'].items())
    records={}
    for d in sorted(root.iterdir()):
        if not (d/'stq-summary.json').exists():continue
        meta=json.loads((d/'metadata.json').read_text());summary=json.loads((d/'stq-summary.json').read_text())
        source=Path(meta['campaign'])/'crypto_kem/ntruplus768'/meta['implementation']
        target=root/'installed-sources'/meta['implementation']
        if not target.exists():shutil.copytree(source,target)
        manifest={str(p.relative_to(target)):sha(p) for p in target.rglob('*') if p.is_file()}
        assert all(sha(source/p)==h for p,h in manifest.items())
        assert sha(d/'measure')==meta['measure_elf_sha256']
        assert sha(Path('/home/nuc/supercop-20260627/crypto_kem/measure.c'))==meta['measure_source_sha256']
        pooled={op:[] for op in ['keypair_cycles','enc_cycles','dec_cycles']};launches=[]
        for path in sorted((d/'fresh-launches').glob('launch-*.out')):
            row={}
            for op in pooled:
                values=decode_observations(path.read_text(),op);assert len(values)==96
                pooled[op]+=values;row[op]=stabilized_quartiles(values)
            launches.append(row)
        assert len(launches)==9
        for op,values in pooled.items():
            assert stabilized_quartiles(values)[1]==summary['operations'][op]['stq2']
        record={'source_manifest':manifest,'elf_sha256':sha(d/'measure'),
                'compiler':summary['measure_identity'],'stq':summary['operations'],'launches':launches,
                'layout':elf_layout(d/'measure',('ntruplus768_keypair_impl','ntruplus768_enc_derand_impl',
                    'ntruplus768_dec_impl','ntruplus768_pack_m_lazy10788_avx2','ntruplus768_pack_m_centered_avx2'))}
        if d.name!='native-official':
            key='m' if 'candidate' in d.name else 'c'
            record['serializer_audit']=audit(d/'measure',d,{key:'ntruplus768_pack_m_lazy10788_avx2'})
        records[d.name]=record
    deltas={}
    for name in ['native-official','native-current']:
        deltas[name]={}
        for op in ['keypair_cycles','enc_cycles','dec_cycles']:
            base=records[name]['stq'][op]['stq2'];new=records['native-candidate']['stq'][op]['stq2']
            ds=[a[op][1]-b[op][1] for a,b in zip(records['native-candidate']['launches'],records[name]['launches'])]
            deltas[name][op]={'delta':new-base,'percent':100*(new-base)/base,
                'index_matched_launch_deltas':ds,'favorable':sum(x<0 for x in ds),
                'note':'sequential independent measurements, NOT balanced paired causal evidence'}
    report={'evidence':records,'native_deltas':deltas,'clean_unchanged':True,'native_measure_unmodified':True,
            'changed_caller':'Encap lazy/highrange only; Decap centered and Keygen P unchanged',
            'automatic_promotion':False}
    if (root/'paired/summary.json').exists():
        report['paired']=json.loads((root/'paired/summary.json').read_text())
        rows=report['paired']['rows']
        primary=next(x for x in rows if x['setting']=='normal-aslr-on' and x['operation']=='enc_cycles')
        regression=[x for x in rows if x['bootstrap_ci95_low']>0]
        off=[x for x in rows if x['setting'].endswith('aslr-off') and x['operation']=='enc_cycles']
        report['gates']={'primary_Encap_CI_below_zero':primary['bootstrap_ci95_high']<0,
            'ASLR_off_Encap_CIs_below_zero':all(x['bootstrap_ci95_high']<0 for x in off),
            'significant_regressions':regression,
            'paired_control_is':'frozen current GT, despite generic official field name',
            'production_qualification':'not passed; no clean promotion'}
    (root/'qualification-summary.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'native_deltas':deltas,'paired_available':'paired' in report},indent=2))
