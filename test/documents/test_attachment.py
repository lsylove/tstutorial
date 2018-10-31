import unittest
import random
import os
from definitions import EDRM_DIR, TEMP_DIR
from test.context import documents, directories, trec, db


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

    def test_process(self):
        export_dir = os.path.join(TEMP_DIR, "test_doc_attachments")
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)
        cached = trec.docids.Cached()
        doc_ids = trec.docids.doc_ids()
        with db.doc_to_dir.Reader() as reader_dir:
            with db.attachment_type.Reader() as reader_attach:
                for n in range(20):
                    doc_id = random.choice(doc_ids)
                    doc_id = cached.find(doc_id)
                    if not documents.attachment.is_attachment(doc_id):
                        continue
                    with reader_dir.open(doc_id) as file:
                        lst = documents.attachment.process(file)
                    self.assertIsNotNone(lst)
                    attachment_type = reader_attach.find(doc_id)
                    if attachment_type == "application/msexcell":
                        seen = set()
                        lst = [w for w in lst if not (w in seen or seen.add(w))]
                    file_dir = os.path.join(export_dir, str(n))
                    with open(file_dir, mode="w", encoding="utf-8") as file:
                        file.write(doc_id + "\n")
                        for token in lst:
                            file.write(token + "\n")


if __name__ == "__main__":
    unittest.main()
