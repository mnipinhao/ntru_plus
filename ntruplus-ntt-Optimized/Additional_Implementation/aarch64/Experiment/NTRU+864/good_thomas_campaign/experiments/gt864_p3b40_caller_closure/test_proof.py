"""Differential sanity checks, not replacements for interval proofs."""
import random,unittest
import prove as p
def mul(a,b):
    product=a*b;t=((product*-12929+32768)%65536)-32768
    n=product+t*3457
    assert -2**31<=n<2**31 and n%65536==0
    return n//65536
def inverse(a):
    t1=mul(a,a);t2=mul(t1,t1);t2=mul(t2,t2);t3=mul(t2,t2)
    t1=mul(t1,t2);t2=mul(t1,t3);t2=mul(t2,t2);t2=mul(t2,a);t1=mul(t1,t2)
    for _ in range(6):t2=mul(t2,t2)
    return p.G.BASE.fixed(mul(t2,t1),(-1571,-14891))
class Tests(unittest.TestCase):
    def test_batch_bound(self):
        rng=random.Random(86440);bound=p.baseinv_bound()['output']
        for case in range(256):
            d=[rng.randrange(-32768,32768) for _ in range(36)]
            if case<4:d=[(-32768,32767,0,1)[case]]*36
            c=[d[0]]
            for v in d[1:]:c.append(mul(c[-1],v))
            if c[-1]==0:continue  # Real C failure branch zeroes the output.
            inv=inverse(c[-1]);out=[0]*36
            for i in range(35,0,-1):out[i]=mul(c[i-1],inv);inv=mul(inv,d[i])
            out[0]=inv
            for v in out:
                for numerator in (-32768,32767,rng.randrange(-32768,32768)):
                    self.assertTrue(bound[0]<=mul(numerator,v)<=bound[1])
    def test_bad_generic_pair_rejected(self):
        with self.assertRaises(AssertionError):p.bm((-31332,-31332),(-31332,-31332))
    def test_asymmetric_corners(self):
        for a in (-32768,32767):
            for b in (0,4095):
                self.assertEqual(len(p.bm((a,a),(b,b),(-32768,32767))),3)
if __name__=='__main__':unittest.main()
