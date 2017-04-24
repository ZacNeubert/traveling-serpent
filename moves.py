#!/usr/bin/python3

from collections import namedtuple
from math import sqrt

MOVETUPLE = namedtuple('TMove', 'delta,reward,name')
DELTATUPLE = namedtuple('TDelta', 'r,c')

class CARDINAL:
    REWARD = -1
    UP = DELTATUPLE(-1, 0)
    RI = DELTATUPLE(0, 1)
    DO = DELTATUPLE(1, 0)
    LE = DELTATUPLE(0, -1)

class DIAGONAL:
    REWARD = -1*sqrt(2)
    UR = DELTATUPLE(-1, 1)
    UL = DELTATUPLE(-1, -1)
    DR = DELTATUPLE(1, 1)
    DL = DELTATUPLE(1, -1)

class MOVES:
    ALL = [MOVETUPLE(CARDINAL.UP, CARDINAL.REWARD, 'UP'),
           MOVETUPLE(CARDINAL.RI, CARDINAL.REWARD, 'RIGHT'),
           MOVETUPLE(CARDINAL.DO, CARDINAL.REWARD, 'DOWN'),
           MOVETUPLE(CARDINAL.LE, CARDINAL.REWARD, 'LEFT'),
           MOVETUPLE(DIAGONAL.UR, DIAGONAL.REWARD, 'UP-RIGHT'),
           MOVETUPLE(DIAGONAL.UL, DIAGONAL.REWARD, 'UP-LEFT'),
           MOVETUPLE(DIAGONAL.DR, DIAGONAL.REWARD, 'DOWN-RIGHT'),
           MOVETUPLE(DIAGONAL.DL, DIAGONAL.REWARD, 'DOWN-LEFT')]

    @classmethod
    def RIGHT(cls):
        return [m for m in cls.ALL if m.delta.c > 0]
    
    @classmethod
    def LEFT(cls):
        return [m for m in cls.ALL if m.delta.c < 0]
    
    @classmethod
    def DOWN(cls):
        return [m for m in cls.ALL if m.delta.r > 0]
    
    @classmethod
    def UP(cls):
        return [m for m in cls.ALL if m.delta.r < 0]

    @classmethod
    def GOOD_ON_LEFT(cls):
        good = [0, 1, 2, 4, 6]
        return [cls.ALL[g] for g in good]
