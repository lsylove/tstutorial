import unittest
from definitions import EDRM_DIR
from .context import db, directories


class TC(unittest.TestCase):
    def tearDown(self):
        db.doc_to_dir.destroy()

    def test_writer_and_reader(self):
        root_dir = directories.general.compose_dir(EDRM_DIR, "Jones", "T", 3)
        with db.doc_to_dir.Writer() as writer:
            def append_kv(doc_file, file_dir):
                doc_file = doc_file.split(".")
                del doc_file[-1]
                writer.add(".".join(doc_file), file_dir)
            directories.general.for_each_file(root_dir, append_kv)
        with db.doc_to_dir.Reader() as reader:
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
