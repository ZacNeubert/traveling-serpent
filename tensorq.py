import argparse
import datetime

import tensorflow as tf
import numpy as np
import time
import pickle

from tensorflow.contrib.layers import sparse_column_with_keys, one_hot_column, embedding_column
from tensorflow.contrib.learn import DNNRegressor

from data import *
from moves import MOVES
from main import flatten

def send_to_redis(fulfilled):
    for request, result in fulfilled.items():
        set_q_value(request, result)


def grid_square_name(row, col):
    return 'GridSquare_row{}_col{}'.format(row, col),


def sparse_feature_cols(rows, cols):
    sparse_cols = []
    for i in range(rows):
        for j in range(cols):
            sparse_cols.append(
                sparse_column_with_keys(
                    column_name=grid_square_name(i, j),
                    keys=[0, 1, 2],
                    # keys=['Empty', 'Player', 'City'],
                    dtype=tf.int32
                ))
    return sparse_cols


def one_hot_for_move_feature_col():
    return [sparse_column_with_keys(
        column_name='Move',
        keys=[i for i, m in enumerate(MOVES.ALL)],
        dtype=tf.int32
    )]


def as_sparse_tensor(li):
    dense_shape = [0, len(li)]
    indices = [[0, i] for i, v in enumerate(li) if v]
    values = [1]
    return tf.SparseTensor(dense_shape=dense_shape, indices=indices, values=values)


def dense_to_sparse(li):
    a = np.array(li)
    with tf.Session() as sess:
        a_t = tf.constant(a)
        idx = tf.where(tf.not_equal(a_t, 0))
        # Use tf.shape(a_t, out_type=tf.int64) instead of a_t.get_shape() if tensor shape is dynamic
        sparse = tf.SparseTensor(idx, tf.gather_nd(a_t, idx), a_t.get_shape())
        dense = tf.sparse_tensor_to_dense(sparse)
        b = sess.run(dense)
        assert np.all(a == b)
    return sparse


CURRENT_REQUESTS = []


def request_input_fn():
    global CURRENT_REQUESTS

    requests = dequeue_n_request()

    if not requests:
        return None, None

    json_requests = [json.loads(state) for state in requests if len(state) == 600]
    CURRENT_REQUESTS = json_requests

    grids = [st['grid'] for st in json_requests]
    moves = [st['move'] for st in json_requests]
    flat_grids = [flatten([flatten(row) for row in grid]) for grid in grids]

    x_li = [grid + move for grid, move in zip(flat_grids, moves)]
    x = tf.constant(x_li)

    return x, None


def training_input_fn():
    redis_train = retrieve_all_train()
    states = [tr['state'] for tr in redis_train]
    qs = tf.constant([tr['q'] for tr in redis_train])

    grids = [st['grid'] for st in states]
    moves = [st['move'] for st in states]
    flat_grids = [flatten([flatten(row) for row in grid]) for grid in grids]

    x_li = [grid + move for grid, move in zip(flat_grids, moves)]
    x = tf.constant(x_li)
    y = qs

    return x, y


TRAIN_EVERY = 90
TRAINING_ITERATIONS = 150

TRAINING_DATA = {}

HIDDEN_UNITS = [156, 52, 26]
FEATURE_COLUMNS = [tf.contrib.layers.real_valued_column("", dimension=156)]

if __name__ == '__main__':
    estimator = None

    tf.logging.set_verbosity(tf.logging.INFO)

    last_train_date = time.time()
    with tf.Session(config=tf.ConfigProto(log_device_placement=True)).as_default():
        while True:
            if time.time() - last_train_date > TRAIN_EVERY or estimator is None:
                estimator = DNNRegressor(
                    feature_columns=FEATURE_COLUMNS,
                    hidden_units=HIDDEN_UNITS
                )

                estimator.fit(input_fn=training_input_fn, max_steps=TRAINING_ITERATIONS)
                tf.get_default_session()
                last_train_date = time.time()

            if len_request():
                results = list(estimator.predict_scores(input_fn=request_input_fn))
                fulfilled = {json.dumps(req, sort_keys=True): res for req, res in zip(CURRENT_REQUESTS, results)}
                send_to_redis(fulfilled)
                print('Fullfilled {} requests'.format(len(results)))
