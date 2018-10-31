import tensorflow as tf
from typing import *


def length(_input: tf.Tensor) -> tf.Tensor:
    used = tf.sign(tf.reduce_max(tf.abs(_input), axis=2))
    ret = tf.reduce_sum(used, axis=1)
    ret = tf.cast(ret, tf.int32)
    return ret


def lstm(_input: tf.Tensor, internal_dims: int, keep_prob: tf.Tensor=tf.constant(0.8)) -> tf.Tensor:
    seq_length = length(_input)
    basic_lstm = tf.nn.rnn_cell.LSTMCell(internal_dims)
    dropout_lstm = tf.nn.rnn_cell.DropoutWrapper(basic_lstm, keep_prob, keep_prob)
    lstm_output, (state_c, state_h) = tf.nn.dynamic_rnn(dropout_lstm, _input,
                                                        sequence_length=seq_length,
                                                        dtype=tf.float32)
    # return tf.reduce_max(lstm_output, axis=[1])
    return state_h


def layer(_input: tf.Tensor, out_shape: int, training_bool: tf.Tensor) -> tf.Tensor:
    weight_init = tf.random_normal_initializer(stddev=(1.0 / out_shape) ** 0.5)
    logits = tf.layers.dense(_input, out_shape, kernel_initializer=weight_init)
    normalized = tf.layers.batch_normalization(logits, momentum=0.9, epsilon=1e-08, training=training_bool)
    normalized = tf.squeeze(normalized)
    return tf.nn.sigmoid(normalized)


def loss(logits: tf.Tensor, labels: tf.Tensor) -> Tuple[tf.Tensor, tf.Tensor, tf.Tensor]:
    cross_entropy = tf.nn.softmax_cross_entropy_with_logits_v2(labels=labels, logits=logits)
    cost = tf.reduce_mean(cross_entropy)
    train_loss_summary_op = tf.summary.scalar("train_cost", cost)
    val_loss_summary_op = tf.summary.scalar("validation_cost", cost)
    return cost, train_loss_summary_op, val_loss_summary_op


def training(cost: tf.Tensor, global_step: tf.Variable, learning_rate: float=0.001) -> tf.Tensor:
    optimizer = tf.train.AdamOptimizer(learning_rate)
    return optimizer.minimize(cost, global_step)


def evaluate(output: tf.Tensor, labels: tf.Tensor, cond: Callable[[float], bool]) -> Tuple[tf.Tensor, tf.Tensor]:
    dif = tf.abs(tf.subtract(output, labels))
    res = tf.map_fn(cond, dif, dtype=tf.bool)
    accuracy = tf.reduce_mean(tf.cast(res, tf.float32))
    accuracy_summary_op = tf.summary.scalar("accuracy", accuracy)
    return accuracy, accuracy_summary_op
