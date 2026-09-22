#!/usr/bin/env python3
"""Fast regression/negative tests; full evidence replay is the generator --check."""
import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'tools'))
import research_gt_vector_mapping as model
import vector_mapping_source_ledger as ledger


class Models(unittest.TestCase):
    def test_macro_definition_order(self):
        # The real pack.s uses .purgem/redefinition. Looking up the last macro
        # in the file incorrectly reads an uninitialized ymm11 in an earlier fn.
        text='''.macro M
vmovdqu (%rsi),%ymm0
.endm
first:
M
ret
.size first,.-first
.purgem M
.macro M
vmovdqu (%rsi),%ymm1
.endm
second:
M
ret
.size second,.-second
'''
        s=ledger.Source(text)
        self.assertIn('%ymm0',s.function('first')[0])
        self.assertIn('%ymm1',s.function('second')[0])

    def test_uninitialized_alias_is_rejected(self):
        with self.assertRaises(AssertionError):
            ledger.stats(['vpaddw %ymm3,%ymm0,%ymm0'])
        result=ledger.stats(['vmovdqu (%rsi),%xmm0','vmovdqu %ymm0,(%rdi)'])
        self.assertEqual(result['peak_live_YMM'],1)

    def test_existing_source_counts(self):
        current=ledger.current_ledger(model.CLEAN)
        wire=ledger.wire_ledger(model.ROOT)
        self.assertEqual(current['frontend']['classes']['routing'],96)
        self.assertEqual(current['Mul']['classes']['data_load_instructions'],132)
        self.assertEqual(current['Mul']['classes']['data_store_instructions'],84)
        self.assertEqual(current['decode']['classes']['routing']-wire['decode']['classes']['routing'],96)
        self.assertEqual(current['pack']['classes']['routing']-wire['pack']['classes']['routing'],192)
        self.assertLessEqual(max(v['peak_live_YMM'] for v in current.values() if isinstance(v,dict)),16)

    def test_whole_vector_renaming_counterexample(self):
        g=model.gt_frontend_geometry()
        self.assertFalse(g['whole_vector_rename_only'])
        self.assertEqual(g['vectors'][0]['source_qwords'],[(0,0,0),(1,0,1),(2,0,2),(0,0,3)])

    def test_all_stage_placements_have_same_residues(self):
        x=[(i*37+11)%model.Q for i in range(96)]
        for s in model.GT.BRANCH_SCALE:
            expected=model.n32.current_transform(x,s)
            for cut in (0,3,4,5):
                actual,_,_=model.partial_transform(x,s,cut)
                self.assertEqual(actual,expected)

    def test_aggregated_lambda_and_missing_companion(self):
        packets,_=model.wire.packet_map()
        p=packets[0]
        c=model.agg.constants(p)
        h=list(range(16))
        r=[i*791-4000 for i in range(16)]
        m=[-i*913 for i in range(16)]
        output,_=model.agg.execute(model.agg.schedule(),h,r,m,c)
        expected=model.agg.reference(h,r,m,p)
        self.assertEqual([x%model.Q for x in output],expected)
        # A factor with an old QINV companion is not an innocuous constant edit.
        bad=copy.deepcopy(c)
        bad['kcomp']=[0]*16
        output,_=model.agg.execute(model.agg.schedule(),h,r,m,bad)
        self.assertNotEqual([x%model.Q for x in output],expected)

    def test_storage_last_packet(self):
        packets,_=model.wire.packet_map()
        report=model.wire.verify_storage(packets)
        self.assertEqual(report['final_byte'],1151)
        self.assertEqual(report['polynomial_sized_new_temporary_bytes'],0)
        self.assertEqual(report['final_packet_store_sizes'],[16,8,4])


if __name__=='__main__':
    unittest.main()
