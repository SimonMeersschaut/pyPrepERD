import unittest
from analysis.processes.transform import read_bparams, read_tof_calibration, process_file

class TestTransform(unittest.TestCase):
    def test_transform(self):
        input_filename = "tests/analysis/processes/transform/ERD25_090_02A.flt"
        tofchmin = 1
        tofchmax = 8192

        B0, B1, B2 = read_bparams("tests/analysis/processes/transform/Bparams.txt", tofchmin, tofchmax)
        ns_ch, t_offs = read_tof_calibration("tests/analysis/processes/transform/Tof.in")
        process_file(input_filename, B0, B1, B2, ns_ch, t_offs, tofchmin, tofchmax)