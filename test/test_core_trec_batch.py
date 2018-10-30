import unittest
import tensorflow as tf
import numpy as np
import threading
import concurrent.futures
from typing import *
from .context import core, db, documents, trec


class TC(tf.test.TestCase):
    @unittest.skip("slow")
    def test_prepare_seed_batch(self):
        ref = [0]
        with db.word_to_vector.Reader() as reader_w2v:
            with db.doc_to_dir.Reader() as reader_d2d:
                with db.attachment_type.Reader() as reader_at:
                    def vectorize(doc_id):
                        ref[0] += 1
                        if ref[0] % 20 == 0:
                            print("So far,", ref[0], "documents processed")
                        with reader_d2d.open(doc_id) as file:
                            if documents.attachment.is_attachment(doc_id):
                                text = documents.attachment.process(file)
                                try:
                                    attachment_type = reader_at.find(doc_id)
                                    if attachment_type == "application/msexcell":
                                        seen = set()
                                        text = [w for w in text if not (w in seen or seen.add(w))]
                                except AttributeError:
                                    pass
                            else:
                                text = documents.message.process(file)
                        ret = reader_w2v.lookup_embedding(text)
                        print(doc_id, ret.shape)
                        return ret
                    cached = trec.seed.Cached()
                    lst = cached.seeds(204)

                    def gen() -> Iterable[Tuple[np.ndarray, np.float32]]:
                        for obj in lst:
                            yield vectorize(obj["doc_id"]), float(obj["relevance"])

                    train, valid = core.trec_batch.prepare_seed_batch(gen)
                    train_batch = train.make_one_shot_iterator().get_next()
                    valid_batch = valid.make_one_shot_iterator().get_next()

                    with self.test_session() as sess:
                        ref[0] = 0
                        try:
                            while True:
                                ref[0] += 1
                                elements = sess.run(train_batch)
                                self.assertEqual(len(elements), 2)
                                print(len(elements[0]), len(elements[0][0]))
                                self.assertEqual(max(elements[0], key=len), min(elements[0], key=len))
                        except tf.errors.OutOfRangeError:
                            train_count = ref[0]
                        ref[0] = 0
                        try:
                            while True:
                                ref[0] += 1
                                elements = sess.run(valid_batch)
                                self.assertEqual(len(elements), 2)
                                print(len(elements[0]), len(elements[0][0]))
                                self.assertEqual(max(elements[0], key=len), min(elements[0], key=len))
                        except tf.errors.OutOfRangeError:
                            valid_count = ref[0]
                        self.assertEqual(train_count, valid_count * 3)

    def test_prepare_seed_batch_preprocessed(self):
        ref = [0]
        with db.word_to_vector.Reader() as reader_w2v:
            with db.doc_to_dir.Reader() as reader_d2d:
                with db.attachment_type.Reader() as reader_at:
                    executor = concurrent.futures.ThreadPoolExecutor(max_workers=6)
                    lock = threading.Lock()
                    q = []

                    def __dispatch(doc_id, rel):
                        with reader_d2d.open(doc_id) as file:
                            if documents.attachment.is_attachment(doc_id):
                                text = documents.attachment.process(file)
                                try:
                                    attachment_type = reader_at.find(doc_id)
                                    if attachment_type == "application/msexcell":
                                        seen = set()
                                        text = [w for w in text if not (w in seen or seen.add(w))]
                                except AttributeError:
                                    pass
                            else:
                                text = documents.message.process(file)
                        vec = reader_w2v.lookup_embedding(text)
                        print(doc_id, vec.shape)
                        with lock:
                            ref[0] += 1
                            if ref[0] % 20 == 0:
                                print("So far,", ref[0], "documents processed")
                            q.append((vec, rel))

                    cached = trec.seed.Cached()
                    lst = cached.seeds(204)

                    # lst2 = [(vectorize(obj["doc_id"]), float(obj["relevance"])) for obj in lst]

                    for obj in lst:
                        executor.submit(__dispatch(obj["doc_id"], obj["relevance"]))

                    def gen() -> Iterable[Tuple[np.ndarray, np.float32]]:
                        for tup in q:
                            yield tup

                    train, valid = core.trec_batch.prepare_seed_batch(gen)
                    train_batch = train.make_one_shot_iterator().get_next()
                    valid_batch = valid.make_one_shot_iterator().get_next()

        with self.test_session() as sess:
            ref[0] = 0
            print("**Training**")
            try:
                while True:
                    elements = sess.run(train_batch)
                    ref[0] += len(elements[0])
                    self.assertEqual(len(elements), 2)
                    print(len(elements[0]), len(elements[0][0]))
                    self.assertEqual(len(max(elements[0], key=len)), len(min(elements[0], key=len)))
            except tf.errors.OutOfRangeError:
                train_count = ref[0]
            ref[0] = 0
            print("**Validation**")
            try:
                while True:
                    elements = sess.run(valid_batch)
                    ref[0] += len(elements[0])
                    self.assertEqual(len(elements), 2)
                    print(len(elements[0]), len(elements[0][0]))
                    self.assertEqual(len(max(elements[0], key=len)), len(min(elements[0], key=len)))
            except tf.errors.OutOfRangeError:
                valid_count = ref[0]
            print("Total # of data in train set:", train_count)
            print("Total # of data in valid set:", valid_count)


if __name__ == "__main__":
    tf.test.main()
