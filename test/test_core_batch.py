import tensorflow as tf
import numpy as np
from typing import *
from .context import core


class TC(tf.test.TestCase):
    @staticmethod
    def mock_embedding(length: int) -> np.ndarray:
        return np.random.uniform(-0.25, 0.25, (length, 8))

    def test_create_dataset(self):
        lst = [("apple", 1.), ("bacon", 0.7), ("cherry", 0.5), ("daisy", 0.8), ("egg", 0.2),
               ("frog", 0.9), ("glue", 0.1), ("hi", 0.), ("i", 0.4), ("john", 0.6)]

        def gen() -> Iterable[Tuple[np.ndarray, np.float32]]:
            for did, rel in lst:
                yield self.mock_embedding(len(did)), rel

        dataset = core.batch.create_dataset(gen, tf.TensorShape([None, 8]))
        it = dataset.make_one_shot_iterator()
        el = it.get_next()

        with self.test_session() as sess:
            for w, r in lst:
                v, r2 = sess.run(el)
                self.assertAlmostEqual(r, r2)
                self.assertEqual(len(w), len(v))

    def test_split_dataset(self):
        lst = [(31, 0.6), (128, 0.4), (63, 0.2), (107, 0.5), (171, 0.6), (3, 0.4), (6, 0.2), (1731, 0.5),
               (64, 0.6), (153, 0.4), (367, 0.2), (5, 0.5), (1, 0.6), (3, 0.4), (81, 0.2), (12, 0.5)]

        def gen() -> Iterable[Tuple[np.ndarray, np.float32]]:
            for did, rel in lst:
                yield self.mock_embedding(did), rel

        dataset = core.batch.create_dataset(gen, tf.TensorShape([None, 8]))
        train, valid = core.batch.split_dataset(dataset, 10)
        train_it = train.make_one_shot_iterator()
        valid_it = valid.make_one_shot_iterator()
        op = train_it.get_next()[1] + train_it.get_next()[1] + train_it.get_next()[1] - valid_it.get_next()[1]

        with self.test_session() as sess:
            for _ in range(3):
                print(sess.run(op))

    def test_bucket_batch_dataset(self):
        lst = [(31, 0.6), (128, 0.4), (63, 0.2), (107, 0.5), (171, 0.6), (3, 0.4), (6, 0.2), (1731, 0.5),
               (64, 0.6), (153, 0.4), (367, 0.2), (5, 0.5), (1, 0.6), (3, 0.4), (81, 0.2), (12, 0.5)]

        def gen() -> Iterable[Tuple[np.ndarray, np.float32]]:
            for did, rel in lst:
                yield self.mock_embedding(did), rel

        dataset = core.batch.create_dataset(gen, tf.TensorShape([None, 8]))
        dataset = core.batch.bucket_batch_dataset(dataset, 2, [1, 10, 20, 50, 100, 200, 500])
        batch = dataset.make_one_shot_iterator().get_next()

        with self.test_session() as sess:
            for _ in range(11):
                elements = sess.run(batch)
                self.assertEqual(len(elements), 2)
                for elt in elements[0]:
                    print(len(elt))


if __name__ == "__main__":
    tf.test.main()
