#!/usr/bin/python3

from os import system
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--iters', type=int, action='store', default=1000)
parser.add_argument('--tf', action='store_true', default=False)
parser.add_argument('-x', type=int, default=10)
parser.add_argument('-y', type=int, default=10)
parser.add_argument('-c', type=int, default=5)
parser.add_argument('--outfile', action='store', required=True)
args = parser.parse_args()

eps = [0.0, .1, .2, .3, .4, .5, .6, .7, .8, .9, 1.0]

if args.tf:
    args.tf = '--tf'
else:
    args.tf = ''

run_str = 'python3 main.py --eps {eps} --iters {iter} {tf} -x {x} -y {y} -c {c}'
no_out_suffix = '| tee out{eps}.txt &'
out_suffix = ' | tee {outfile}'

for e in eps:
    print(e)
    no_out_str = run_str+no_out_suffix
    no_out_str = no_out_str.format(eps=e, x=args.x, y=args.y, c=args.c, tf=args.tf, iter=args.iters)
    print(no_out_str)
    system(no_out_str)

out_str = (run_str + out_suffix).format(eps=0.05, x=args.x, y=args.y, c=args.c, tf=args.tf, iter=args.iters, outfile=args.outfile)
print(out_str)
system(out_str)
