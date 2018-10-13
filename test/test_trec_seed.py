import unittest
from .context import trec


class TC(unittest.TestCase):
    def test_seeds(self):
        lst = trec.seed.seeds(204)
        lst = [obj["doc_id"] for obj in lst]
        self.assertEqual(len(lst), 1229)
        self.assertTrue("3.359528.J23XFU5UJKNXE5OA3RBIWESIRRBNFTPKB.1" in lst)
        self.assertFalse("3.359901.HTOLAPJVK4UQYYDRNZB2KQSO1TUNMYEVA" in lst)

    def test_cached_seeds(self):
        cached = trec.seed.Cached()
        lst1 = cached.seeds(204)
        lst1 = [obj["doc_id"] for obj in lst1 if obj["relevance"] == 1]
        lst2 = trec.seed.seeds(204)
        lst2 = [obj["doc_id"] for obj in lst2 if obj["relevance"] == 1]
        self.assertEqual(len(lst1), 59)
        self.assertEqual(len(lst2), 59)
        self.assertTrue("3.412507.MVHLOLN1F5W2OMV3NFSMU1ZUN4BGJY12A.1" in lst1)
        self.assertTrue("3.413361.O0PXTDRTHU12XEHQOYPXMO5SRZD1GNBJB.1" in lst2)

    def test_cached_seed_object(self):
        cached = trec.seed.Cached()
        obj = cached.seed_object("3.415789.J11DGR1MCBC42MEUHILSP1L4PIT52EUAB.1")
        self.assertEqual(obj["req_id"], 205)
        self.assertEqual(obj["doc_id"], "3.415789.J11DGR1MCBC42MEUHILSP1L4PIT52EUAB.1")
        self.assertEqual(obj["relevance"], 0)
        obj = cached.seed_object("3.419946.KIEVIEZWTDSAICTEKRKQLAQMYPVZX4VOB.1")
        self.assertEqual(obj["req_id"], 203)
        self.assertEqual(obj["doc_id"], "3.419946.KIEVIEZWTDSAICTEKRKQLAQMYPVZX4VOB.1")
        self.assertEqual(obj["relevance"], -1)
        obj = cached.seed_object("foo.bar")
        self.assertIsNone(obj)


if __name__ == "__main__":
    unittest.main()
