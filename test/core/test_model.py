import unittest
import tensorflow as tf
import numpy as np
import os
from typing import *
from definitions import TEMP_DIR
from test.context import core


class TC(tf.test.TestCase):
    def test_lstm(self):
        mock_data = np.random.uniform(-0.25, 0.25, (640, 100, 8)).astype(np.float32)
        dataset = tf.data.Dataset.from_tensor_slices(mock_data)
        dataset = dataset.batch(batch_size=32)
        it = dataset.make_one_shot_iterator()

        x = it.get_next()
        output = core.model.lstm(x, 22)
        init_op = tf.global_variables_initializer()

        with self.test_session() as sess:
            sess.run(init_op)
            ref = [0]
            try:
                while True:
                    res = sess.run(output)
                    ref[0] += 1
                    shape = tf.shape(res)
                    self.assertEqual(shape[0].eval(), 32)
                    self.assertEqual(shape[1].eval(), 22)
            except tf.errors.OutOfRangeError:
                pass
            self.assertEqual(ref[0], 20)

    @unittest.skip
    def test_loss(self):
        def gen() -> Iterator[Tuple[np.ndarray, np.float32]]:
            for idx in range(100):
                vec = np.random.uniform(-0.25, 0.25, (idx, 64))
                yield vec, np.add.reduce(np.add.reduce(vec))

        dataset = core.batch.create_dataset(gen, tf.TensorShape([None, 64]))
        dataset = core.batch.bucket_batch_fixed_size(dataset, 16, [0, 50, 100])
        it = dataset.make_one_shot_iterator()

        global_step = tf.Variable(0, name="global_step", trainable=False)

        x, y = it.get_next()
        lstm_output = core.model.lstm(x, 32)
        output = core.model.layer(lstm_output, 1, tf.constant(True))
        cost, _, _ = core.model.loss(output, y)
        train_op = core.model.training(cost, global_step)

        init_op = tf.global_variables_initializer()

        i = 0

        with self.test_session() as sess:
            sess.run(init_op)
            try:
                while True:
                    _, new_cost = sess.run([train_op, cost])
                    i += 1
                    print("Cost at Batch {0}: {1:.4f}".format(i, new_cost))
            except tf.errors.OutOfRangeError:
                self.assertEqual(i, 8)

    def test_basic_model(self):
        def gen() -> Iterator[Tuple[np.ndarray, np.float32]]:
            for idx in range(1000):
                vec = np.random.uniform(-0.25, 0.25, (idx // 10, 64))
                yield vec, 1. if np.add.reduce(np.add.reduce(vec)) > 0 else 0.

        epoch = 200

        dataset = core.batch.create_dataset(gen, tf.TensorShape([None, 64]))
        val, tra = core.batch.split_dataset(dataset, 150, 100)
        tra = core.batch.bucket_batch_fixed_size(tra, 128, [0, 50, 100])
        val = core.batch.bucket_batch_fixed_size(val, 256, [0, 100])

        it = tf.data.Iterator.from_structure(tra.output_types, tra.output_shapes)
        tra_init_op = it.make_initializer(tra)
        val_init_op = it.make_initializer(val)

        global_step = tf.Variable(0, name="global_step", trainable=False)
        training_bool = tf.placeholder(tf.bool)
        keep_prob = tf.placeholder(tf.float32)

        x, y = it.get_next()
        lstm_output = core.model.lstm(x, 32, keep_prob=keep_prob)
        output = core.model.layer(lstm_output, 1, training_bool)
        cost, train_loss_summary_op, val_loss_summary_op = core.model.loss(logits=output, labels=y)
        accuracy, accuracy_summary_op = core.model.evaluate(output, y, lambda v: v < 0.25)

        train_op = core.model.training(cost, global_step)
        extra_update_ops = tf.get_collection(tf.GraphKeys.UPDATE_OPS)

        init_op = tf.global_variables_initializer()

        with self.test_session() as sess:
            log_dir = os.path.join(TEMP_DIR, "tb")
            summary_writer = tf.summary.FileWriter(log_dir, graph=sess.graph)

            sess.run(init_op)
            for i in range(epoch):
                print("Epoch #", i + 1)
                sess.run(tra_init_op)
                while True:
                    try:
                        _, _, train_summary = sess.run([train_op, extra_update_ops, train_loss_summary_op],
                                                       feed_dict={training_bool: True,
                                                                  keep_prob: 0.8})
                        summary_writer.add_summary(train_summary, sess.run(global_step))
                    except tf.errors.OutOfRangeError:
                        sess.run(val_init_op)
                        val_summary, val_loss_summary = sess.run([accuracy_summary_op, val_loss_summary_op],
                                                                 feed_dict={training_bool: False,
                                                                            keep_prob: 1.})
                        summary_writer.add_summary(val_summary, sess.run(global_step))
                        summary_writer.add_summary(val_loss_summary, sess.run(global_step))
                        break


if __name__ == "__main__":
    tf.test.main()
