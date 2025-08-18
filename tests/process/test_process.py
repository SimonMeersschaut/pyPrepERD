import unittest
import process
import shutil
import os


class TestProcess(unittest.TestCase):
    def test_folder_structure(self):
        if os.path.exists("tests/process/output"):
            shutil.rmtree("tests/process/output")
        
        os.mkdir("tests/process/output")
        self.assertTrue(os.path.exists("tests/process/output"))

        # copy .flt file
        shutil.copyfile("tests/process/ERD16_075_01A.lst", "tests/process/output/ERD16_075_01A.lst")

        # run process
        process.handle_folder("tests/process/output")

        self.assertTrue(os.path.exists("tests/process/output/ERD16_075_01A.evt.png"))
        self.assertTrue(os.path.exists("tests/process/output/ERD16_075_01A.mvt.png"))

        self.assertTrue(os.path.exists("tests/process/output/01A/Tof.in"))

        self.assertTrue(os.path.exists("tests/process/output/01A/ERD16_075_01A.evt.flt"))
        self.assertTrue(os.path.exists("tests/process/output/01A/ERD16_075_01A.mvt.flt"))

        self.assertTrue(os.path.exists("tests/process/output/01A/ERD16_075_01A.lst"))