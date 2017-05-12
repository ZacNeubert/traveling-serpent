#!/usr/bin/python3

import json
import random
from time import sleep

import redis

# Redis
from main import Grid

r = redis.StrictRedis(host='localhost', port=6379, db=0)


def get_str(key):
    result = r.get(key)
    return result.decode('UTF-8') if result else None


def get_int(key):
    result = r.get(key)
    return int(result) if result else None


def get_float(key, no_set=False):
    result = r.get(key)
    if result:
        return float(result)
    else:
        if not no_set:
            r.set(key, 0.5)
        return 0.5


def get_action_array(a):
    return [1 if a == i else 0 for i in list(range(9))]


def get_key(s, a):
    if isinstance(s, Grid):
        s = s.get_state()
    return json.dumps({'grid': s.get_state(), 'move': get_action_array(a)}, sort_keys=True)


# region Queues
REQUEST_Q_KEY = 'REDIS_Q_KEY'
RQK = REQUEST_Q_KEY
TRAIN_Q_KEY = 'TRAIN_Q_KEY'
TQK = TRAIN_Q_KEY


def delete_request():
    r.delete(RQK)


def len_request():
    return r.llen(RQK)


def enqueue_request(key):
    r.rpush(RQK, key)


def get_or_enqueue_range(grid, moves, sleep_time=.01):
    #print('Asking for {} states'.format(len(moves)))
    results = [None for move in moves]
    for i, move in enumerate(moves):
        key = get_key(grid, move)
        result = r.get(key)
        if result is not None:
            results[i] = float(result)
        else:
            enqueue_request(get_key(grid, move))
    while None in results:
        for i, move in enumerate(moves):
            if results[i] is None:
                result = r.get(get_key(grid, move))
                if result is not None:
                    results[i] = float(result)
        sleep(sleep_time)
    return results


def get_or_enqueue(state, sleep_time=.01):
    #print('Asking for state')
    result = r.get(state)
    if not result:
        enqueue_request(state)
    while not result:
        result = r.get(state)
        sleep(sleep_time)
    return float(result)


def dequeue_request():
    return r.lpop(RQK).decode('UTF-8')


def dequeue_n_request(n=50000):
    items = []
    for _ in range(n):
        item = r.lpop(RQK)
        if not item:
            return items
        items.append(item.decode('UTF-8'))
    return [json.loads(it) for it in items]


def delete_train():
    r.delete(TQK)


def len_train():
    return r.hlen(TQK)


def enqueue_train(state, action, q):
    if isinstance(state, Grid):
        state = state.get_state()
    key = get_key(state, action)
    r.hset(TQK, key, q)


def retrieve_all_train():
    train = r.hgetall(TQK)
    train_deserialized = [{'state': json.loads(key.decode('UTF-8')), 'q': float(val)} for key, val in train.items()]
    return train_deserialized  # Check format


def set_q_value(state, q, expire=90):
    r.set(state, q, expire)


# endregion

if __name__ == '__main__':
    delete_request()
    delete_train()

    for s in range(100):
        enqueue_request(str(s))

    result = dequeue_n_request()
    assert len(result) == 50
    assert result[0] == '0'
    assert len(dequeue_n_request()) == 50

    for s in range(100):
        enqueue_train('abc', 123)

    result = dequeue_n_train()
    assert len(result) == 50
    assert type(result[0]) is dict
    assert result[0]['state'] == 'abc'
    assert result[0]['q'] == 123

    for s in range(100):
        enqueue_request(str(s))
    for s in range(100):
        enqueue_train('abc', 123)

    clear_queues()

    set_q_value('abc', 123, 10)
    assert get_int('abc')
    sleep(11)
    assert not get_int('abc')
