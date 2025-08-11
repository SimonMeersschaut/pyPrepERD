import unittest
from analysis import load_bparams_file, load_tof_file, extend_flt_data, load_flt_file


class TestTransform(unittest.TestCase):
    def test_load_bparams(self):
        B0, B1, B2 = load_bparams_file("tests/analysis/transform/Bparams.txt")

        # read expected values
        with open("tests/analysis/transform/Bparams.txt", 'r') as f:
            expected_lines = f.read().split('\n')[:-1] # remove empty line at end of file
        expected_lines = [None] + [[float(val) for val in line.split(' ')[2:5]] for line in expected_lines]
        # please note that index 0 is unused and will be empty (both for `expected_lines`, as for B0, B1 and B2).

        self.assertEqual(len(B0), len(expected_lines),"The length of `B0` was not as expected.")
        self.assertEqual(len(B1), len(expected_lines),"The length of `B1` was not as expected.")
        self.assertEqual(len(B2), len(expected_lines),"The length of `B2` was not as expected.")

        for i in range(1, len(expected_lines)):
            self.assertEqual(expected_lines[i][0], B0[i], f"Line {i}, value 0 was unexpected.")
            self.assertEqual(expected_lines[i][1], B1[i], f"Line {i}, value 1 was unexpected.")
            self.assertEqual(expected_lines[i][2], B2[i], f"Line {i}, value 2 was unexpected.")
        
    def test_load_tof_file(self):
        ns_ch, t_offs = load_tof_file("tests/analysis/transform/Tof.in")

        self.assertEqual(5.82033E-11, ns_ch, "`ns_ch` not the expected result.")
        self.assertEqual(-4.28867E-09, t_offs, "`t_offs` not the expected result.")
    
    def test_load_flt_data(self):
        """
        """
        flt_data = load_flt_file("tests/analysis/transform/ERD25_090_02A.flt")

        self.assertEqual(680089, len(flt_data), "Length of flt_data was unexpected.")
        
        # TODO: test all output
    
    def test_extend_flt_data(self):
        """
        """
        flt_data = load_flt_file("tests/analysis/transform/ERD25_090_02A.flt")
        B0, B1, B2 = load_bparams_file("tests/analysis/transform/Bparams.txt")
        ns_ch, t_offs = load_tof_file("tests/analysis/transform/Tof.in")
        extended_data = extend_flt_data(flt_data, B0, B1, B2, ns_ch, t_offs)

        # read expected result
        with open("tests/analysis/transform/ERD25_090_02A.ext", 'r') as f:
            ext_expected_lines = f.read().split('\n')[:-1]
        
        # test equality
        self.assertEqual(len(flt_data), len(extended_data), "Nunber of lines did not match expected value.")
        self.assertEqual(len(ext_expected_lines), len(extended_data), "Nunber of lines did not match expected value.")

        for i in range(len(ext_expected_lines)):
            # exp = ext_expected_lines[i].split(' ')
            # comp = [x for x in ext_computed_lines[i].split(' ') if len(x) > 0]
            ToFch, ToFns, Ench, Iso_amu, Iso_ch = extended_data
            tested_line = f"{ToFch:7d} {ToFns:12.3f} {Ench:7d} {Iso_amu:11.4f} {Iso_ch:7d}\n"
            self.assertEqual(ext_expected_lines[i], tested_line, f"Line {i} did not match the expected output.")