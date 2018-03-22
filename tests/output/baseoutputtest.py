import os
import pypact as pp

from tests.testerbase import Tester, REFERENCE_DIR


class BaseOutputUnitTest(Tester):
    def setUp(self):
        self.base_dir = os.path.join(REFERENCE_DIR)
        self.filename_test91out = os.path.join(self.base_dir, "test91.out")
        self.filerecord91 = pp.FileRecord(self.filename_test91out)
        self.filename_test31out = os.path.join(self.base_dir, "test31.out")
        self.filerecord31 = pp.FileRecord(self.filename_test31out)
