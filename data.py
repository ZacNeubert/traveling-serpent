#!/usr/bin/python3

import random
import redis

# Redis
r = redis.StrictRedis(host='localhost', port=6379, db=0)

def get_str(key):
    return r.get(key).decode('UTF-8')

def get_int(key):
    return int(r.get(key))

def get_float(key):
    v = r.get(key)
    if v:
        return float(r.get(key))
    else:
        v = 0.5
        r.set(key, v)
        return v

def get_key(s, a):
    return s.get_state() + str(a)
