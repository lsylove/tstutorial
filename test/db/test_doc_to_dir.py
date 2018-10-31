import unittest
from definitions import EDRM_DIR
from test.context import db, directories

TEST_DIR = db.doc_to_dir.DIR.replace("data", "mock")


class TC(unittest.TestCase):
    def tearDown(self):
        db.doc_to_dir.destroy(db_dir=TEST_DIR)

    def test_writer_and_reader(self):
        root_dir = directories.general.compose_dir(EDRM_DIR, "Jones", "T", 3)
        with db.doc_to_dir.Writer(db_dir=TEST_DIR) as writer:
            def append_kv(doc_file, file_dir):
                doc_id = directories.general.doc_file_to_doc_id(doc_file)
                writer.add(doc_id, file_dir)
            directories.general.for_each_file(root_dir, append_kv)
        with db.doc_to_dir.Reader(db_dir=TEST_DIR) as reader:
            doc_dir = reader.find("3.895108.GWNQE50LK05TT0ZDOYGNC2AYEZHC4LRXA")
            self.assertIsNotNone(doc_dir)
            doc_dir = reader.find("3.895118.BC04OO3EQFCDAK05IQSI3ZXQXFZ30XABA.1")
            self.assertIsNotNone(doc_dir)
            with open(doc_dir) as file:
                file.readline()
                line = file.readline()
                self.assertEqual(line.strip().lower(), "ge power systems")


if __name__ == "__main__":
    unittest.main()
