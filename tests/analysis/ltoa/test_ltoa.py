import unittest
import analysis

import numpy as np
import os

class TestLtoa(unittest.TestCase):
    def test_load_lst_file(self):
        flt_computed_lines = analysis.load_lst_file("tests/analysis/ltoa/ERD16_075_01A.lst")

        with open("tests/analysis/ltoa/expected.flt", 'r') as f:
            flt_expected_lines = f.read().split(' \n')
        
        # parse lines
        flt_expected_lines = [[int(val) for val in line.split(' ')] for line in flt_expected_lines[:-1]] # remove empty line at end of file
        flt_expected_lines = np.asarray(flt_expected_lines)
        
        self.assertEqual(flt_computed_lines.shape[1], 2, f"Unexpected shape of output array, expected (n, 2), got (n, {flt_computed_lines.shape[1]}).")
        self.assertEqual(len(flt_expected_lines), len(flt_computed_lines), "Nunber of lines did not match expected value.")

        for i in range(len(flt_expected_lines)):
            for j in range(flt_computed_lines.shape[1]):
                self.assertEqual(flt_expected_lines[i][j], flt_computed_lines[i][j], f"Line {i}, element {j} did not match the expected output.")

    def test_file_not_exist(self):
        self.assertRaises(FileNotFoundError, lambda: analysis.load_lst_file("tests/analysis/ltoa/this_file_does_not_exist.lst"))
    
    def test_wrong_extension(self):
        self.assertRaises(NameError, lambda: analysis.load_lst_file("tests/analysis/ltoa/expected.flt"))
    
    def test_dump_flt_file(self):
        flt_computed_lines = analysis.load_lst_file("tests/analysis/ltoa/ERD16_075_01A.lst")

        analysis.dump_flt_file(flt_computed_lines, "tests/analysis/ltoa/output.flt")

        self.assertTrue(os.path.exists("tests/analysis/ltoa/output.flt"), "Output file was not found.")

        # Compare outputs
        with open("tests/analysis/ltoa/output.flt", 'r') as f:
            output_lines = f.read().split('\n')
        
        with open("tests/analysis/ltoa/expected.flt", 'r') as f:
            expected_lines = f.read().split('\n')
        
        self.assertEqual(len(expected_lines), len(output_lines), "Nunber of lines did not match expected value.")

        for i in range(len(expected_lines)):
                self.assertEqual(expected_lines[i], output_lines[i], f"Line {i}  did not match the expected output.")
