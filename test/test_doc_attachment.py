import unittest
from definitions import EDRM_DIR
from .context import documents, directories


class TC(unittest.TestCase):
    def test_attachment_types(self):
        d1 = directories.general.compose_dir(EDRM_DIR, "Allen", "P")
        d2 = directories.general.compose_dir(EDRM_DIR, "Arnold", "J")
        res = set()

        def build_set(_, file_dir):
            with open(file_dir, encoding="utf-8") as file:
                types = documents.attachment.parse_attachment_types(file)
                for type_id in types:
                    res.add(type_id)

        for d in [d1, d2]:
            directories.general.for_each_file(d, build_set)

        self.assertEqual(len(res), 9)
        self.assertCountEqual(res, {
            "application/msexcell", "application/msword", "application/pdf", "application/mspowerpoint",
            "application/octet-stream", "application/rtf", "image/gif", "image/jpeg", "image/bmp"
        })


if __name__ == "__main__":
    unittest.main()
