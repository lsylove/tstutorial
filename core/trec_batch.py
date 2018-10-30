import tensorflow as tf
import numpy as np
from typing import *
import core.batch

DATASET_APPROX_SIZE = 1200


def prepare_seed_batch(gen: Callable[[], Iterable[Tuple[np.ndarray, np.float32]]],
                       val_ratio: float=0.25,
                       batches: List[int]=list((128, 128, 128, 64, 64, 64, 64, 32, 32, 32, 32, 16, 16, 16, 16, 16, 16)),
                       boundaries: List[int]=list((0, 10, 25, 50, 75, 100, 250, 500, 750, 1000, 2500, 5000, 7500,
                                                   10000, 15000, 20000))) -> \
        Tuple[tf.data.Dataset, tf.data.Dataset]:
    dataset = core.batch.create_dataset(gen, tf.TensorShape([None, 301]))
    val, tra = core.batch.split_dataset(dataset, int(val_ratio * DATASET_APPROX_SIZE), DATASET_APPROX_SIZE)
    val = core.batch.bucket_batch_dataset(val, batches, boundaries)
    tra = core.batch.bucket_batch_dataset(tra, batches, boundaries)
    return tra, val
