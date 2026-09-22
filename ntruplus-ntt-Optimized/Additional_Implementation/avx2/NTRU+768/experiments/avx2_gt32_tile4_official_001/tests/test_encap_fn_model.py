#!/usr/bin/env python3
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/"tools"))
from generate_encap_fn_eager import CLEAN, Source, build, dag_outputs
import json

class Model(unittest.TestCase):
    def test_proof_and_allocation(self):
        _,text=build()
        x=json.loads(text)
        self.assertTrue(x["range_certificate"]["identical_arithmetic_expression_multiset"])
        self.assertEqual(x["ownership"]["lambda_identities_verified"],192)
        self.assertEqual(len(x["ownership"]["all_768_owners"]),768)
        self.assertEqual(x["class_delta"]["data_store_instructions"],-36)
        self.assertEqual(x["class_delta"]["data_load_instructions"],-36)
        self.assertEqual(x["class_delta"].get("constant_memory_operands"),0)
        self.assertEqual(x["candidate_ledger"]["peak_live_YMM"],16)

    def test_wrong_constant_is_not_accepted(self):
        source=(CLEAN/"basemul.s").read_text()
        base=Source(source).function("ntruplus768_basemul_general_m_avx2")
        wrong=[x.replace(".Ltile4_bm_rsq(", ".Ltile4_bm_q(") for x in base]
        self.assertNotEqual(dag_outputs(base)[0],dag_outputs(wrong)[0])

if __name__=="__main__":
    unittest.main()
