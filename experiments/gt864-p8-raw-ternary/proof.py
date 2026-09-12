"""Exhaustive integer model of each signed 16-bit Neon arithmetic step."""
import json
from pathlib import Path
def oracle(x):
    centered=(x+1728)%3457-1728
    return (centered+1)%3-1
def candidate(x):
    hi=-int(x>1728);lo=-int(x < -1728)
    a=x+hi-lo
    t=(a*10923+16384)//32768
    y=a-3*t
    assert -32768<=a<=32767 and -32768<=t<=32767
    return y
for x in range(-4577,4578):assert candidate(x)==oracle(x),x
# Also determine the exact reusable contiguous range, not a full-int16 claim.
b=4577
while candidate(b+1)==oracle(b+1) and candidate(-b-1)==oracle(-b-1):b+=1
assert b==5185
report=dict(status='pass',inputs=9155,input_bound=4577,valid_symmetric_bound=b,
    counterexample_next=dict(x=b+1,expected=oracle(b+1),candidate=candidate(b+1)),
    intermediate_bound=4576,output_bound=1,scale='natural R0 to centered ternary')
Path(__file__).with_name('proof.json').write_text(json.dumps(report,indent=2)+'\n')
print(report)
