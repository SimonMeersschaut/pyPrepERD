import time
import unittest
from analysis.transform import read_bparams, read_tof_calibration, process_file

class TestTransform(unittest.TestCase):
    def test_transform(self):
        # read expected result
        with open("tests/analysis/transform/ERD25_090_02A.ext", 'r') as f:
            ext_expected_lines = f.read().split('\n')[:-1]
        
        input_filename = "tests/analysis/transform/ERD25_090_02A.flt"
        output_filename = "tests/analysis/transform/output.ext"
        tofchmin = 1
        tofchmax = 8192

        B0, B1, B2 = read_bparams("tests/analysis/transform/Bparams.txt", tofchmin, tofchmax)
        ns_ch, t_offs = read_tof_calibration("tests/analysis/transform/Tof.in")
        process_file(input_filename, output_filename, B0, B1, B2, ns_ch, t_offs, tofchmin, tofchmax)

        time.sleep(1)

        # read output file
        with open(output_filename, 'r') as f:
            ext_computed_lines = f.read()[:-1].split('\n')

        # test equality
        self.assertEqual(len(ext_expected_lines), len(ext_computed_lines), "Nunber of lines did not match expected value.")

        for i in range(len(ext_expected_lines)):
            exp = ext_expected_lines[i].split(' ')
            comp = [x for x in ext_computed_lines[i].split(' ') if len(x) > 0]
            # if exp != com:
                
            self.assertEqual(exp, comp, f"Line {i} did not match the expected output.")