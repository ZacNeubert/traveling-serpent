#!/usr/bin/python3

import json
import random
from time import sleep

import redis

# Redis
r = redis.StrictRedis(host='localhost', port=6379, db=0)


def get_str(key):
    result = r.get(key)
    return result.decode('UTF-8') if result else None


def get_int(key):
    result = r.get(key)
    return int(result) if result else None


def get_float(key):
    result = r.get(key)
    if result:
        return float(result)
    else:
        r.set(key, 0.5)
        return 0.5


def get_key(s, a):
    return s.get_state() + str(a)


# region Queues
REQUEST_Q_KEY = 'REDIS_Q_KEY'
RQK = REQUEST_Q_KEY
TRAIN_Q_KEY = 'TRAIN_Q_KEY'
TQK = TRAIN_Q_KEY


def delete_request():
    r.delete(RQK)


def len_request():
    return r.llen(RQK)


def enqueue_request(state):
    r.rpush(RQK, state)


def get_or_enqueue(state, sleep_time=.1):
    result = r.get(state)
    if not result:
        enqueue_request(state)
    while not result:
        result = r.get(state)
        sleep(sleep_time)
    return result


def dequeue_request():
    return r.lpop(RQK).decode('UTF-8')


def dequeue_n_request(n=50):
    items = []
    for _ in range(n):
        item = r.lpop(RQK)
        if not item:
            return items
        items.append(item.decode('UTF-8'))
    return items


def delete_train():
    r.delete(TQK)


def len_train():
    return r.llen(TQK)


def enqueue_train(state, q):
    r.rpush(TQK, json.dumps({'state': state, 'q': q}))


def dequeue_train():
    obj = json.loads(r.lpop(TQK).decode('UTF-8'))
    return obj['state'], obj['q']


def dequeue_n_train(n=50):
    items = []
    for _ in range(n):
        item = r.lpop(TQK)
        if not item:
            return items
        items.append(json.loads(item.decode('UTF-8')))
    return items


def process_queues(process_requests, process_training, endc):
    while True:
        requests = dequeue_n_request()
        process_requests(requests)
        training = dequeue_n_train()
        process_training(training)
        if endc(len_request(), len_train()):
            return


def print_all(li):
    for l in li:
        print(l)


def print_print_queues():
    process_queues(print_all, print_all, lambda re, tr: re == tr == 0)


def nothing(n):
    pass


def clear_queues():
    process_queues(nothing, nothing, lambda re, tr: re == tr == 0)


def set_q_value(state, q, expire=90):
    r.set(state, q)
    r.expire(state, expire)


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

    print('You good brah')

    for s in range(100):
        enqueue_request(str(s))
    for s in range(100):
        enqueue_train('abc', 123)

    clear_queues()

    set_q_value('abc', 123, 10)
    assert get_int('abc')
    sleep(11)
    assert not get_int('abc')
