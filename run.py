import tensorflow as tf
import numpy as np
import sys
import os
import queue
import multiprocessing
import concurrent.futures
import threading
import core.trec_batch
import core.model
import db.word_to_vector
import db.doc_to_dir
import documents.attachment
import documents.message
import trec.seed
from typing import *
from definitions import TEMP_DIR


def __dispatch_for_mvs(doc_id, rel, file_dir, q, v, lock):
    with open(file_dir, "r", encoding="utf-8") as file:
        if documents.attachment.is_attachment(doc_id):
            text = documents.attachment.process(file)
            seen = set()
            text = [w for w in text if not (w in seen or seen.add(w))]
        else:
            text = documents.message.process(file)
        q.put((text, rel))
        with lock:
            v.value += 1
            value = v.value
        if value % 20 == 0:
            print(value, "Files Processed")


def mock_validation_with_seeds(req_id: int) -> None:
    with multiprocessing.Pool(processes=os.cpu_count() - 2) as pool:
        m = multiprocessing.Manager()
        q = m.Queue()
        va = m.Value("i", 0)
        lock = m.Lock()

        lst = trec.seed.seeds(req_id)
        with db.doc_to_dir.Reader() as reader_dd:
            lst = [(obj["doc_id"], obj["relevance"], reader_dd.find(obj["doc_id"])) for obj in lst]
        future_lst = []
        for tup in lst:
            try:
                fut = pool.apply_async(__dispatch_for_mvs, (tup[0], tup[1], tup[2], q, va, lock))
                future_lst.append(fut)
                fut.get(timeout=0.000001)
            except multiprocessing.TimeoutError:
                pass

    print("***Reading***")

    with db.word_to_vector.Reader() as reader_wv:
        ref = [0]
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=24)
        inner_lock = threading.Lock()
        lst2 = []

        def __dispatch_inner(text, rel2):
            vec = reader_wv.lookup_embedding(text)
            with inner_lock:
                lst2.append((vec, rel2))
                ref[0] += 1
                refer = ref[0]
            if refer % 20 == 0:
                print(refer, "Files Appended")

        while True:
            try:
                next_text, rel = q.get(timeout=1)
                executor.submit(__dispatch_inner(next_text, rel))
            except queue.Empty:
                break

    def gen() -> Iterable[Tuple[np.ndarray, np.float32]]:
        for tup2 in lst2:
            yield tup2

    print("***Start Training***")

    with tf.Session().as_default() as sess:
        epoch = 200

        tra, val = core.trec_batch.prepare_seed_batch(gen, val_ratio=0.2)
        it = tf.data.Iterator.from_structure(tra.output_types, tra.output_shapes)
        tra_init_op = it.make_initializer(tra)
        val_init_op = it.make_initializer(val)

        global_step = tf.Variable(0, name="global_step", trainable=False)
        training_bool = tf.placeholder(tf.bool)
        keep_prob = tf.placeholder(tf.float32)

        x, y = it.get_next()
        lstm_output = core.model.lstm(x, 64, keep_prob=keep_prob)
        output = core.model.layer(lstm_output, 1, training_bool)
        cost, train_loss_summary_op, val_loss_summary_op = core.model.loss(logits=output, labels=y)
        accuracy, accuracy_summary_op = core.model.evaluate(output, y, lambda v: v < 0.25)

        train_op = core.model.training(cost, global_step)
        extra_update_ops = tf.get_collection(tf.GraphKeys.UPDATE_OPS)

        init_op = tf.global_variables_initializer()

        log_dir = os.path.join(TEMP_DIR, "mvs_" + str(req_id))
        summary_writer = tf.summary.FileWriter(log_dir, graph=sess.graph)

        accuracy_put = tf.placeholder(tf.float32)
        accuracy_scalar = tf.summary.scalar("accuracy_", accuracy_put)
        val_loss_put = tf.placeholder(tf.float32)
        val_loss_scalar = tf.summary.scalar("validation_cost_", val_loss_put)

        sess.run(init_op)
        for i in range(epoch):
            print("Epoch #", i + 1)
            sess.run(tra_init_op)
            while True:
                try:
                    _, _, train_summary = sess.run([train_op, extra_update_ops, train_loss_summary_op],
                                                   feed_dict={training_bool: True,
                                                              keep_prob: 0.85})
                    summary_writer.add_summary(train_summary, sess.run(global_step))
                except tf.errors.OutOfRangeError:
                    if i % 2 == 0:
                        sess.run(val_init_op)
                        accuracies = []
                        losses = []
                        while True:
                            try:
                                acc, cos = sess.run([accuracy, cost], feed_dict={training_bool: False, keep_prob: 1.})
                                accuracies.append(acc)
                                losses.append(cos)
                            except tf.errors.OutOfRangeError:
                                accuracy_mean = np.mean(np.array(accuracies).astype(np.float32))
                                loss_mean = np.mean(np.array(losses).astype(np.float32))
                                summary_writer.add_summary(sess.run(accuracy_scalar,
                                                                    feed_dict={accuracy_put: accuracy_mean}),
                                                           sess.run(global_step))
                                summary_writer.add_summary(sess.run(val_loss_scalar,
                                                                    feed_dict={val_loss_put: loss_mean}),
                                                           sess.run(global_step))
                                break
                    break


def main(argv: List[str]) -> None:
    if len(argv) < 3:
        raise ValueError("Too few arguments")
    try:
        {
            "mvs": mock_validation_with_seeds
        }[argv[1]](int(argv[2]))
    except ValueError:
        raise ValueError("Invalid argument #1")
    except KeyError:
        raise ValueError("Invalid argument #0")


if __name__ == '__main__':
    main(sys.argv)
