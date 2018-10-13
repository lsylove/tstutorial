import unittest
from .context import directories


class TC(unittest.TestCase):
    def test_author_to_zipdir(self):
        zip_dir = directories.author.author_to_zipdir("Allen", "P")
        self.assertEqual(zip_dir, "edrm-enron-v2_allen-p_xml.zip")
        zip_dir = directories.author.author_to_zipdir("Kaminski", "V", 1, 2)
        self.assertEqual(zip_dir, "edrm-enron-v2_kaminski-v_xml_1of2.zip")
        zip_dir = directories.author.author_to_zipdir("Kean", "S", 5, 8)
        self.assertEqual(zip_dir, "edrm-enron-v2_kean-s_xml_5of8.zip")

    def test_zipdir_to_author(self):
        author, fi, _, _ = directories.author.zipdir_to_author("edrm-enron-v2_allen-p_xml.zip")
        self.assertEqual(author, "Allen")
        author, fi, seq, fin = directories.author.zipdir_to_author("edrm-enron-v2_kaminski-v_xml_1of2.zip")
        self.assertEqual(author, "Kaminski")
        self.assertEqual(seq, 1)
        author, fi, seq, fin = directories.author.zipdir_to_author("edrm-enron-v2_kean-s_xml_5of8.zip")
        self.assertEqual(fi, "S")
        self.assertEqual(seq, 5)
        self.assertEqual(fin, 8)


if __name__ == "__main__":
    unittest.main()
