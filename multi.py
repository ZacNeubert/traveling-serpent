#!/usr/bin/python3

from os import system
from sys import argv

if '--tf' in argv:
    tf = '--tf'
else:
    tf = ''

eps = [0.0, .1, .2, .3, .4, .5, .6, .7, .8, .9, 1.0]

for e in eps:
    print(e)
    system('python3 main.py --eps {} --iter 10 {} | tee out{}.txt &'.format(e, tf, e))

system('python3 main.py --eps 0.0 --iter 10 {} --verbose'.format(tf))
