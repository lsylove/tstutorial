import tensorflow as tf
from typing import *


def lstm_with_layer_norm(_input: tf.Tensor, internal_dims: int, keep_prob: float=0.8) -> tf.Tensor:
    lstm = tf.contrib.rnn.LayerNormBasicLSTMCell(internal_dims,
                                                 dropout_keep_prob=keep_prob)
    lstm_output, _ = tf.nn.dynamic_rnn(lstm, _input, dtype=tf.float32)
    return tf.reduce_max(lstm_output, axis=[1])
