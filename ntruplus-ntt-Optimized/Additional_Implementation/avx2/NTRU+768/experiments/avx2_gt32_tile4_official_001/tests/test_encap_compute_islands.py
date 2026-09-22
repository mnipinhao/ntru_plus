"""Regression tests for the machine-source compute-island gate."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import gate_encap_compute_islands as gate


class ComputeIslandGate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = gate.build()

    def test_output_retention_exceeds_current_register_schedule(self):
        a = self.report["A_live_B3_to_ciphertext"]
        self.assertEqual(a["source_loop_peak_YMM"], 16)
        self.assertEqual([r["counterfactual_peak"] for r in
                          a["retain_results_with_identical_instruction_schedule"][:2]],
                         [17, 18])
        self.assertEqual(len(a["first_three_output_store_instruction_indices"]), 3)

    def test_m_blocks_and_caller_ownership(self):
        b = self.report["B_live_m_terminal_to_MulAdd"]
        self.assertEqual(b["forward_loop_iterations"] * b["M_blocks_per_iteration"], 12)
        self.assertEqual(b["planes_per_block"] * 12, 48)
        self.assertLess(max(b["first_block_store_instruction_indices"]),
                        min(b["second_block_store_instruction_indices"]))
        self.assertEqual(self.report["range_contract"]["refined_post_add_abs_bound"], 17448)

    def test_historical_control_is_not_a_new_candidate(self):
        old = self.report["historical_controls"]["serializer_side_sum_m"]
        self.assertLess(old["normal_full_encap_tsc_delta"], 0)
        self.assertGreater(old["reversed_full_encap_tsc_delta"], 0)
        self.assertEqual(self.report["prototype_decision"].split()[0], "zero")


if __name__ == "__main__":
    unittest.main()
