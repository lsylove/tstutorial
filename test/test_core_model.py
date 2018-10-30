import tensorflow as tf
import numpy as np
from .context import core


class TC(tf.test.TestCase):
    def test_lstm_with_layer_norm(self):
        mock_data = np.random.uniform(-0.25, 0.25, (640, 100, 8)).astype(np.float32)
        dataset = tf.data.Dataset.from_tensor_slices(mock_data)
        dataset = dataset.batch(batch_size=32)
        it = dataset.make_one_shot_iterator()

        x = it.get_next()
        y = core.model.lstm_with_layer_norm(x, 22)
        init_op = tf.initialize_all_variables()

        with self.test_session() as sess:
            sess.run(init_op)
            ref = [0]
            try:
                while True:
                    res = sess.run(y)
                    ref[0] += 1
                    shape = tf.shape(res)
                    self.assertEqual(shape[0].eval(), 32)
                    self.assertEqual(shape[1].eval(), 22)
            except tf.errors.OutOfRangeError:
                pass
            self.assertEqual(ref[0], 20)


if __name__ == "__main__":
    tf.test.main()
