#!/usr/bin/python3

from os import system

eps = [0.0, .1, .2, .3, .4, .5, .6, .7, .8, .9, 1.0]

for e in eps:
    print(e)
    system('python3 main.py --eps {} --iter 1001 | tee out{}.txt &'.format(e, e))
