"""Attribute PIE samples by DSO offset -> linked object -> public entry."""
from pathlib import Path
import collections,json,re,statistics,sys
R=Path(__file__).resolve().parent;B=R/'.build'
d=json.loads((R/'measurements-summary.json').read_text())
def nm(text,global_only=False):
    out={}
    for line in text.splitlines():
        m=re.match(r'^([0-9a-f]+)\s+([Tt])\s+(.*)$',line)
        if m and (not global_only or m[2]=='T'):out[m[3]]=int(m[1],16)
    return out
def maps(variant):
    ranges=[];section=''
    for line in (B/(variant+'.map')).read_text().splitlines():
        m=re.match(r'^ (\.text\S*)\s*(.*)',line)
        if m:section=m[1];tail=m[2]
        elif section and re.match(r'^\s+0x',line):tail=line.strip()
        else:section='';continue
        m=re.match(r'(0x[0-9a-f]+)\s+(0x[0-9a-f]+)\s+(.+\.o)$',tail)
        if m:
            start,size=int(m[1],16),int(m[2],16);owner=m[3]
            if size:ranges.append((start,start+size,owner))
        if tail:section=''
    return sorted(ranges)
def category(source,symbol):
    s=symbol.lower();f=source.lower()
    if 'fips202' in f or 'symmetric.c' in f:return 'Hash/SHAKE'
    if 'checked_ct_f_basemul' in s or 'frombytes_basemul_decap_scale' in s or 'decap_packed64' in f:return 'Fused checked decode + first basemul'
    if 'baseinv' in s or 'fqinv' in s or 'baseinv' in f:return 'Base inversion'
    if 'invntt' in s:return 'Inverse NTT'
    if 'ntt' in s or f.endswith('/ntt.s') or f=='ntt.s' or 'decap_forward' in f:return 'Forward NTT'
    if 'basemul_add' in s or 'encap_muladd' in f:return 'Basemul-add'
    if 'basemul' in s or 'decap_base' in f:return 'Base multiplication'
    if 'frombytes' in s or f.endswith('/unpack.s'):return 'Checked unpack'
    if 'tobytes' in s or 'pack.s' in f:return 'Packing'
    if 'cbd' in s:return 'CBD sampling'
    if 'sotp' in s:return 'SOTP encode/decode'
    if 'crepmod3' in s:return 'Centered mod3'
    if 'sub' in s or 'triple' in s:return 'Polynomial support'
    if 'randombytes' in s:return 'Benchmark RNG'
    if 'explicit_bzero' in s or 'memset' in s:return 'Clear/memory runtime'
    if f=='poly.c':return 'Base inversion'
    return 'KEM glue / runtime / unresolved'
out={'method':'Self samples, object/address based; Keygen uses cpu-clock:u at 997Hz, Encap/Decap use cycles:u period 100003. Separate unsampled PMU totals. No call-time instrumentation; percentages are estimates.','profiles':{}}
for variant in ['GT','Official']:
    ranges=maps(variant);syms=nm(d[variant+'-symbols']);objs=d['objects'][variant]
    entries={obj:sorted((syms[name],name) for name in nm(info['symbols'],True) if name in syms) for obj,info in objs.items()}
    out['profiles'][variant]={}
    for mode in ['Keygen','Encap','Decap']:
        reps=[];allgroups=collections.Counter();allfiles=collections.Counter();allentries=collections.Counter();total=0
        for run in d['runs']:
            if run['variant']!=variant or run['mode']!=mode:continue
            tag=run['tag'];counts=collections.Counter();files=collections.Counter();hits=collections.Counter();sample_count=0
            for line in (B/(tag+'-samples.txt')).read_text().splitlines():
                m=re.match(r'\s*[0-9a-f]+\s+(.*?)\s+\((.*)\)\s*$',line)
                if not m:continue
                symbol,dso=m[1],m[2];source='external/runtime';entry=symbol
                offset=re.search(r'/'+variant+r'/workload\+0x([0-9a-f]+)$',dso)
                if offset:
                    addr=int(offset[1],16)
                    matches=[x for x in ranges if x[0]<=addr<x[1]]
                    assert len(matches)<=1,(hex(addr),matches)
                    if matches:
                        obj=matches[0][2];source=objs.get(obj,{}).get('source',obj)
                        eligible=[x for x in entries.get(obj,[]) if x[0]<=addr and x[0]>=matches[0][0]]
                        if eligible:entry=eligible[-1][1]
                c=category(source,entry)
                counts[c]+=1;files[source]+=1;hits[(source,entry)]+=1;sample_count+=1
            counters={}
            for suffix in ['core','memory']:
                for line in (B/(tag+'-'+suffix+'.csv')).read_text().splitlines():
                    parts=line.split(',')
                    if len(parts)>4 and parts[0].isdigit():
                        assert float(parts[4])>=99.9,('multiplexed',tag,line)
                        counters[parts[2]]=int(parts[0])/run['operations']
            reps.append({'rep':run['rep'],'samples':sample_count,'pmu_per_operation':counters,'percent':{k:v/sample_count*100 for k,v in counts.items()}})
            # Equal workload weight per repetition, not higher weight for the
            # smaller sampling period. Retain actual sample count separately.
            allgroups.update({k:v/sample_count for k,v in counts.items()})
            allfiles.update({k:v/sample_count for k,v in files.items()})
            allentries.update({k:v/sample_count for k,v in hits.items()});total+=sample_count
        if not reps:continue
        out['profiles'][variant][mode]={'sample_event':'cpu-clock:u 997Hz' if mode=='Keygen' else 'cycles:u period 100003','sample_count':total,'repetitions':reps,
          'pmu_p50':{k:statistics.median(r['pmu_per_operation'][k] for r in reps) for k in reps[0]['pmu_per_operation']},
          'components':{k:{'percent':v/len(reps)*100,'rep_min':min(r['percent'].get(k,0) for r in reps),'rep_max':max(r['percent'].get(k,0) for r in reps)} for k,v in allgroups.most_common()},
          'files':{k:v/len(reps)*100 for k,v in allfiles.most_common()},
          'entries':[{'source':k[0],'entry':k[1],'percent':v/len(reps)*100} for k,v in allentries.most_common()]}
(R/'profile-summary.json').write_text(json.dumps(out,indent=2)+'\n')
for variant,modes in out['profiles'].items():
    for mode,r in modes.items():
        print(variant,mode,r['pmu_p50'])
        print({k:round(v['percent'],2) for k,v in r['components'].items()})
