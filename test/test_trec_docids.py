import unittest
from .context import trec


class TC(unittest.TestCase):
    def test_doc_ids(self):
        doc_ids = trec.docids.doc_ids()
        self.assertEqual(doc_ids[3], "3.1000065.D2M301CFHC2HMASPQRHGTH3GT0JNYH3GA_0449f0428879cf25e20209856515d6b1")
        self.assertEqual(doc_ids[6], "3.1000065.D2M301CFHC2HMASPQRHGTH3GT0JNYH3GA_58fb8794bee36bc566394e2988e49cab")
        self.assertEqual(len(doc_ids), 685592)

    def test_for_each_doc(self):
        reference = {
            "count": 0
        }

        def find_substr(doc_id):
            if doc_id.find("TLTJ") != -1:
                reference["count"] += 1

        trec.docids.for_each_doc(find_substr)
        self.assertEqual(reference["count"], 10)

    def test_cached_find(self):
        cached = trec.docids.Cached()



if __name__ == "__main__":
    unittest.main()
