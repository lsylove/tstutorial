import tensorflow as tf
import numpy as np
from typing import *


def create_dataset(gen: Callable[[], Iterable[Tuple[np.ndarray, np.float32]]], gen_output_shape: tf.TensorShape) -> \
        tf.data.Dataset:
    return tf.data.Dataset.from_generator(generator=gen,
                                          output_shapes=(gen_output_shape, []),
                                          output_types=(tf.float32, tf.float32))


def split_dataset(dataset: tf.data.Dataset, left_size: int, buffer_size: int=1000) -> \
        Tuple[tf.data.Dataset, tf.data.Dataset]:
    dataset.shuffle(buffer_size=buffer_size)
    return dataset.take(left_size), dataset.skip(left_size)


def bucket_batch_dataset(dataset: tf.data.Dataset, batches: List[int], boundaries: List[int]) -> tf.data.Dataset:
    op = tf.contrib.data.bucket_by_sequence_length(element_length_func=lambda x, y: tf.shape(x)[0],
                                                   bucket_batch_sizes=batches,
                                                   bucket_boundaries=boundaries)
    return dataset.apply(op)


def bucket_batch_fixed_size(dataset: tf.data.Dataset, batch_size: int, boundaries: List[int]) -> tf.data.Dataset:
    batches = [batch_size] * (len(boundaries) + 1)
    return bucket_batch_dataset(dataset, batches, boundaries)
