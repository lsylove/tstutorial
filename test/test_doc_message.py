import unittest
import random
import os
from definitions import TEMP_DIR
from .context import documents, trec, db


class TC(unittest.TestCase):
    def test_process(self):
        export_dir = os.path.join(TEMP_DIR, "test_doc_messages")
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)
        cached = trec.docids.Cached()
        doc_ids = trec.docids.doc_ids()
        with db.doc_to_dir.Reader() as reader:
            for n in range(20):
                doc_id = random.choice(doc_ids)
                doc_id = cached.find(doc_id)
                if not documents.message.is_message(doc_id):
                    continue
                with reader.open(doc_id) as file:
                    try:
                        lst = documents.message.process(file)
                    except AssertionError:
                        print("Drop Header Failure: ", doc_id)
                        continue
                self.assertIsNotNone(lst)
                file_dir = os.path.join(export_dir, str(n))
                with open(file_dir, mode="w", encoding="utf-8") as file:
                    file.write(doc_id + "\n")
                    for token in lst:
                        file.write(token + "\n")


if __name__ == "__main__":
    unittest.main()
