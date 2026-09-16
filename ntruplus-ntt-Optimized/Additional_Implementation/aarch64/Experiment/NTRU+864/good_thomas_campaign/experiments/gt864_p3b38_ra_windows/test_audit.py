"""Negative controls for the independent exact-DAG/address audit."""
import unittest
import run_pi as r

class AuditTest(unittest.TestCase):
    def test_ra_equivalence(self):
        self.assertEqual(r.fingerprint(r.instructions(r.B/'candidate.sym.S')),
                         r.fingerprint(r.instructions(r.B/'allocated.S')))

    def test_arithmetic_corruption(self):
        original = r.instructions(r.B/'candidate.sym.S')
        changed = original.copy()
        i = next(i for i,x in enumerate(changed) if x.startswith('mul '))
        changed[i] = changed[i].replace('mul ', 'sub ', 1)
        self.assertNotEqual(r.fingerprint(original)['outputs'],r.fingerprint(changed)['outputs'])

    def test_address_corruption(self):
        original = r.instructions(r.B/'candidate.sym.S')
        changed = original.copy()
        i = next(i for i,x in enumerate(changed) if x.startswith('ldp '))
        changed[i] = changed[i].replace('#0]', '#16]')
        self.assertNotEqual(r.fingerprint(original)['outputs'],r.fingerprint(changed)['outputs'])
        self.assertNotEqual(r.fingerprint(original)['accesses'],r.fingerprint(changed)['accesses'])

if __name__ == '__main__':
    unittest.main()
