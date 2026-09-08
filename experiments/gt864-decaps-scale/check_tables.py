import pathlib,re,json
root=pathlib.Path(__file__).resolve().parents[2]
old=(root/'ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864/gt864_fr0_inverse_barrett_tables.h').read_text()
new=pathlib.Path(__file__).with_name('scaled_tables.h').read_text()
def table(s,name):
    return list(map(int,re.findall(r'-?\d+',s.split(name+'[16][2][8] = {')[1].split('};')[0])))
q=3457
def centered(x):return (x+1728)%q-1728
max_output=0
for name in ['gt864_inverse16_main_scale_barrett','gt864_inverse16_tail_scale_barrett']:
    a,b=table(old,name),table(new,name)
    assert len(a)==len(b)==256
    for off in range(0,256,16):
        for lane in range(8):
            c=b[off+lane];hat=b[off+8+lane]
            assert c==centered(a[off+lane]*65536)
            assert hat==(c*32768+1728)//q
            for x in range(-32768,32768):
                z=x*c-((x*hat+16384)//32768)*q
                assert -32768<=z<=32767
                max_output=max(max_output,abs(z))
assert max_output*2<32768 # inverse-top subtraction after these constants
assert (3*4095**2+32768*q)/65536<2497
print(json.dumps(dict(table_identity='pass',final_scale_abs_bound=max_output,
    first_decaps_redc_abs_bound=2497,
    caveat='unchanged inverse prefix inherits M5E; not full source-to-binary proof'),indent=2))
