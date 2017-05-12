#!/usr/bin/python3

from os import system

for i in range(2, 5):
    run_str = 'python3 multi.py -x {x} -y {y} -c {c} --outfile extraneousout5x5x{f}tf.txt'.format(x=7, y=7, c=i, f=i-1)
    print(run_str)
    system(run_str)
