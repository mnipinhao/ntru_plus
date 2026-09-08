"""Bound/scale checks for conservative BINV-FR0-0, not a compiler proof."""
import hashlib,json,pathlib
Q,R=3457,65536
def signed(x): return (x+32768)%65536-32768
def center(x):
    # SQRDMULH signed halfword; no saturation case with multiplier 9.
    x=signed(x-((x*9+16384)//32768)*Q)
    if x<0:x+=Q
    if x>1728:x-=Q
    return x
for x in range(-32768,32768):
    y=center(x)
    assert -1728<=y<=1728 and (x-y)%Q==0
assert (R*2775)%Q==1 and R%Q==3310 and R*R%Q==867
assert (-12929*Q)%R==R-1
# Every multiplication receives centered operands, including table zetas.
product_bound=1728**2
redc_numerator_bound=product_bound+32768*Q
assert redc_numerator_bound<2**31
assert redc_numerator_bound/R<1775
assert 2*1728<32768  # each add/sub is immediately centered
# Lazy variant induction: every mm <=2000 for operands <=4000;
# sums/differences contain at most TWO mm outputs, hence <=4000.
# prefix seeds are denominator sums <=4000; later products <=2000.
# Final prefix entries therefore represent field zero iff integer zero.
assert (4000**2+32768*Q)/R<2000
assert 4000<32768
# Exhaust all possible integer products in the enclosing interval. REDC is
# a function of the product alone, so this is stronger than testing pairs.
max_redc=0
for p in range(-product_bound,product_bound+1):
    t=signed(p*(-12929))
    n=p+t*Q
    assert n%R==0
    z=n//R
    max_redc=max(max_redc,abs(z))
    assert -32768<=z<=32767 and (z*R-p)%Q==0
    assert -1728<=center(z)<=1728
src=pathlib.Path(__file__).with_name('baseinv.c')
print(json.dumps(dict(scope='explore; intrinsic arithmetic bounds, not binary CT proof',
    q=Q,internal_scale='R1',output_scale='R0',center_exhaustive=65536,
    product_interval=[-product_bound,product_bound],redc_abs_max=max_redc,
    source_sha256=hashlib.sha256(src.read_bytes()).hexdigest()),indent=2))
