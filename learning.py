from copy import deepcopy

from data import *
from moves import MOVES
from strategy import random_strat

ALPHA = .1  # learning rate, usually small
DISCOUNT = .95  # Discount Rate, usually near 1


def learn(player, cargs=None):
    if not cargs:
        raise Exception('Dude, where my cargs at')

    eps = cargs.eps
    s = deepcopy(player.grid)
    a = eps_choice(player, eps, s, cargs)
    move = MOVES.ALL[a].name
    if cargs and cargs.verbose:
        print(move)

    r = player.move(a)
    if len(player.grid.cities) < len(s.cities):
        r += 100
    if len(player.grid.cities) == 0:
        r += 1000

    s_prime = player.grid
    q = Q(s, a, cargs.tf)
    max_q = max(all_Q(s_prime, cargs.tf))
    new_q = q + ALPHA * (r + DISCOUNT * max_q - q)
    if cargs and cargs.tf:
        enqueue_train(s, a, new_q)
    else:
        setQ(s, a, new_q, cargs.tf)

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

        qvals = all_Q(s, cargs.tf)

        choice = qvals.index(max(qvals))
        if cargs.verbose:
            print(qvals)
            print(choice, qvals[choice])
        return choice


def all_Q(s, tf):
    if tf:
        #qvals = [get_or_enqueue(get_key(s, i)) for i in range(0, 8)]
        qvals = get_or_enqueue_range(s, list(range(0, 8)))
    else:
        qvals = [get_float(get_key(s, i)) for i in range(0, 8)]
    return qvals


def labeled_all_Q(s, tf):
    qvals = all_Q(s, tf)
    lab = []
    for i, q in enumerate(qvals):
        lab.append((MOVES.ALL[i].name, q))
    return lab


def Q(s, a, tf):
    if tf:
        return get_or_enqueue(get_key(s, a))
    else:
        key = get_key(s, a)
        q = get_float(key)
        return q


def setQ(s, a, q, tf):
    if not tf:
        key = get_key(s, a)
        r.set(key, q)
    enqueue_train(s, a, q=q)
