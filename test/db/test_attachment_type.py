import unittest
from definitions import EDRM_DIR
from test.context import db, directories, documents

TEST_DIR = db.attachment_type.DIR.replace("data", "mock")


class TC(unittest.TestCase):
    def tearDown(self):
        db.attachment_type.destroy(db_dir=TEST_DIR)

    def test_writer_and_reader(self):
        root_dir = directories.general.compose_dir(EDRM_DIR, "Allen", "P")
        prev_marker = [False]
        with db.attachment_type.Writer(db_dir=TEST_DIR) as writer:
            def append_kv(doc_file, file_dir):
                doc_id = directories.general.doc_file_to_doc_id(doc_file)
                if documents.attachment.is_attachment(doc_id):
                    prev_marker[0] = True
                    return
                elif not prev_marker[0]:
                    return
                prev_marker[0] = False
                with open(file_dir, encoding="utf-8") as file:
                    types = documents.attachment.parse_attachment_types(file)
                    for i, v in enumerate(types):
                        attachment_id = ".".join([doc_id, str(i + 1)])
                        writer.add(attachment_id, v)
            directories.general.for_each_file(root_dir, append_kv)
        with db.attachment_type.Reader(db_dir=TEST_DIR) as reader:
            attachment_type = reader.find("3.819027.P0IHU1RSVVKDPEMTB3ZVIZBA0XY5L0D0B.1")
            self.assertEqual(attachment_type, "application/msexcell")
            attachment_type = reader.find("3.819069.L32RB4HEIXT2FSBDG0YPRLCEKRDVLVMTB.3")
            self.assertEqual(attachment_type, "application/msexcell")
            attachment_type = reader.find("3.819234.CSUJUIGZLLRJZUBQDZGF1UIGSZRKMLXHB.2")
            self.assertEqual(attachment_type, "image/gif")


if __name__ == "__main__":
    unittest.main()
