import unittest
from analysis.processes.ltoa import LtoaParser

MAX_NADC = 16
ADC_SIZE = 2  # bytes per ADC value
NFBYTES = 1048576  # 1 MB
TXTFILE = "output.txt"
MAXEVENT = 1000000

class TestLtoaParser(unittest.TestCase):
    def test_ltoa_parser(self):
        # read expected result
        with open("tests/analysis/processes/ltoa/expected.txt", 'r') as f:
            flt_expected_lines = f.read().split(' \n')[:-1]

        # Generate cumputed result
        df = LtoaParser("tests/analysis/processes/ltoa/ERD16_075_01A.lst")
        flt_computed_lines = df.parse() #.split('\n')

        # test equality
        self.assertEqual(len(flt_expected_lines), len(flt_computed_lines), "Nunber of lines did not match expected value.")

        for i in range(len(flt_expected_lines)):
            self.assertEqual(flt_expected_lines[i], flt_computed_lines[i], f"Line {i} did not match the expected output.")
        
    def test_file_not_exist(self):
        self.assertRaises(FileNotFoundError, lambda: LtoaParser("tests/analysis/processes/ltoa/this_file_does_not_exist.lst"))