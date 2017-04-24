#!/usr/bin/python3

from random import randint
from moves import *

# Helpers
def distance(a, b):
    return sqrt((a.r - b.r)**2 + (a.c - b.c)**2)

def is_above(a, b):
    return a.r < b.r

def is_below(a, b):
    return a.r > b.r

def is_right(a, b):
    return a.c > b.c

def is_left(a, b):
    return a.c < b.c

#Strategies
def random_strat(player, cargs=None):
    return randint(0,len(MOVES.ALL)-1)

def nearest_city(player, cargs=None):
    grid = player.grid
    cities = grid.cities

    distances = sorted([(c, distance(c, player)) for c in cities], key=lambda k: k[1])

    if cargs.verbose:
        print(distances)
    closest = distances[0][0]

    possible_moves = list(range(0, len(MOVES.ALL)))
    if is_right(closest, player):
        if cargs.verbose:
            print('is_right')
        possible_moves = [p for p in possible_moves if MOVES.ALL[p] in MOVES.RIGHT()]

    if is_left(closest, player):
        if cargs.verbose:
            print('is_left')
        possible_moves = [p for p in possible_moves if MOVES.ALL[p] in MOVES.LEFT()]
    
    if is_above(closest, player):
        if cargs.verbose:
            print('is_above')
        possible_moves = [p for p in possible_moves if MOVES.ALL[p] in MOVES.UP()]
    
    if is_below(closest, player):
        if cargs.verbose:
            print('is_below')
        possible_moves = [p for p in possible_moves if MOVES.ALL[p] in MOVES.DOWN()]

    if cargs.verbose:
        print(possible_moves)
    return possible_moves[0]
