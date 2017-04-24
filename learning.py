from copy import deepcopy

from data import *
from moves import MOVES
from strategy import random_strat

ALPHA = .1  # learning rate, usually small
DISCOUNT = .95  # Discount Rate, usually near 1


def learn(player, cargs=None):
    eps = cargs.eps
    s = deepcopy(player.grid)
    a = eps_choice(player, eps, s, cargs)
    move = MOVES.ALL[a].name
    r = player.move(a)
    if len(player.grid.cities) < len(s.cities):
        r += 1000
    s_prime = player.grid
    q = Q(s, a)
    max_q = max(all_Q(s_prime))
    new_q = q + ALPHA * (r + DISCOUNT * max_q - q)

    setQ(s, a, new_q)

    if cargs.verbose:
        print('Q Change: {}, {}, {}'.format(q, new_q, new_q - q))

    return r


def eps_choice(player, eps, s, cargs=None):
    if random.uniform(0, 1) < eps:
        if cargs.verbose:
            print('Random')
        return random_strat(player, cargs)
    else:
        if cargs.verbose:
            print('Q-based')
        qvals = all_Q(s)

        choice = qvals.index(max(qvals))
        if cargs.verbose:
            print(qvals)
            print(choice, qvals[choice])
        return choice


def all_Q(s):
    qvals = [get_float(get_key(s, i)) for i in range(0, 8)]
    return qvals


def labeled_all_Q(s):
    qvals = all_Q(s)
    lab = []
    for i, q in enumerate(qvals):
        lab.append((MOVES.ALL[i].name, q))
    return lab

def Q(s, a):
    key = get_key(s, a)
    q = get_float(key)
    return q


def setQ(s, a, q):
    key = get_key(s, a)
    r.set(key, q)
