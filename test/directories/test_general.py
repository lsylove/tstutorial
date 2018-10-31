import unittest
from definitions import EDRM_DIR
from test.context import directories


class TC(unittest.TestCase):
    def test_compose(self):
        doc_id = "3.819066.FKMSDEWWCIFPEA3HZ5WAZG1TGTSAPJVYB.1"
        doc_dir = directories.general.compose(EDRM_DIR, doc_id, "Allen", "P")
        with open(doc_dir) as file:
            line = file.readline()
            self.assertEqual(line.strip(), "Stagecoach Apartments")

    def test_for_each_file(self):
        reference = {
            "total": 0,
            "countA": 0,
            "countB": 0
        }

        def find_substr(doc_file, file_dir):
            reference["total"] += 1
            if reference["total"] % 10000 == 0:
                print(reference["total"])
            if file_dir.find("TLTJ") != -1:
                reference["countA"] += 1
            if doc_file.find("TLTJ") != -1:
                reference["countB"] += 1

        directories.general.for_each_file(EDRM_DIR, find_substr)
        self.assertEqual(reference["total"], 685592)
        self.assertEqual(reference["countA"], 10)
        self.assertEqual(reference["countB"], 10)


if __name__ == "__main__":
    unittest.main()
