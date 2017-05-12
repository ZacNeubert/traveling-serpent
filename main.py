#!/usr/bin/python3

import argparse
import sys
from copy import deepcopy
from time import sleep

from moves import *
from output import Output
from prettyprint import *
from strategy import *

parser = argparse.ArgumentParser()
parser.add_argument('--verbose', action='store_true')
parser.add_argument('--eps', type=float, action='store')
parser.add_argument('--iters', type=int, action='store', default=1000)
parser.add_argument('--tf', action='store_true', default=False)
parser.add_argument('--seed', action='store_true', default=False)
parser.add_argument('--static-method', action='store_true', default=False)
parser.add_argument('-x', type=int, default=10)
parser.add_argument('-y', type=int, default=10)
parser.add_argument('-c', type=int, default=5)
cargs = parser.parse_args()


class Player:
    def __init__(self, r, c, grid, strat):
        self.r = r
        self.c = c
        self.grid = grid
        self.strat = strat
        self.grid.move_to(self.r, self.c)

    def move(self, n):
        m = MOVES.ALL[n]
        new_r = self.r + m.delta.r
        new_c = self.c + m.delta.c
        if self.grid.in_bounds(new_r, new_c):
            self.r = new_r
            self.c = new_c
            self.grid.move_to(self.r, self.c)
            if cargs.verbose:
                print(new_r, new_c, m.reward)
            return m.reward
        else:  # Out of bounds
            if cargs.verbose:
                print('Out Of Bounds')
            return 100 * m.reward  # Penalty for leaving the board

    def move_strat(self, cargs=None):
        n = self.strat(self, cargs=cargs)
        return self.move(n), n


class City:
    def __init__(self, r, c, grid):
        self.r = r
        self.c = c
        self.grid = grid

    def __str__(self):
        return 'r{}, c{}'.format(self.r, self.c)

    def __repr__(self):
        return 'r{}, c{}'.format(self.r, self.c)


class Grid:
    EMPTY = 0
    PLAYER = 1
    CITY = 2
    OBSERVED = 3

    COLORGUIDE = {
        0: lambda j: str(j),
        1: lambda j: asYellow(str(j)),
        2: lambda j: asBlue(str(j)),
        3: lambda j: asRed(str(j))
    }

    def __init__(self, rows, cols, cities):
        self.rows = rows
        self.cols = cols
        self.grid = [[0 for i in range(cols)] for j in range(rows)]
        self.cities = []
        for c in range(cities):
            crow, ccol = self.random_non_city()
            self.grid[crow][ccol] = self.CITY
            self.cities.append(City(crow, ccol, self))
        self.player_coords = None

    def random_square(self):
        crow = randint(0, self.rows - 1)
        ccol = randint(0, self.cols - 1)
        return crow, ccol

    def random_non_city(self):
        crow, ccol = self.random_square()
        while self.grid[crow][ccol] == self.CITY:
            crow, ccol = self.random_square()
        return crow, ccol

    def random_city(self):
        return self.cities[randint(0, len(self.cities) - 1)]

    def in_bounds(self, r, c):
        return r >= 0 and r < len(self.grid) and c >= 0 and c < len(self.grid[0])

    def move_to(self, r, c):
        if self.player_coords:
            self.grid[self.player_coords[0]][self.player_coords[1]] = self.EMPTY
        self.player_coords = (r, c)
        self.grid[r][c] = self.PLAYER
        self.cities = [cit for cit in self.cities if cit.r != r or cit.c != c]

    def solved(self):
        for col in self.grid:
            if self.CITY in col:
                return False
        return True

    def __str__(self):
        return '\n'.join([''.join([self.COLORGUIDE[j](j) for j in col]) for col in self.grid])

    def get_state(self):
        return grid_to_cat_columns(self.grid)
        #indices, values, shape = grid_to_sparse_tensor(self.grid)
        #return {'indices': indices, 'values': values, 'shape': shape}

def flatten(twod):
    return [j for i in twod for j in i]

def grid_to_cat_columns(grid):
    return [[[1 if i == x else 0 for i in range(3)] for x in y] for y in grid]


def cat_columns_to_sparse_tensor(cat_cols):
    indices = []
    for i, row in enumerate(cat_cols):
        for j, cat_col in enumerate(row):
            for k, value in enumerate(cat_col):
                if value:
                    indices.append([j, i, k])  # Me and google have disagreements about 2D arrays
    values = flatten(flatten([[[v for v in cat_col if v] for cat_col in row] for row in cat_cols]))
    shape = [len(cat_cols), len(cat_cols[0]), len(cat_cols[0][0])]
    return indices, values, shape


def grid_to_sparse_tensor(grid):
    cat_cols = grid_to_cat_columns(grid)
    return cat_columns_to_sparse_tensor(cat_cols)


if __name__ == '__main__':
    from learning import learn

    total_rewards = []
    total_moves = []
    i = 0
    while True:
        g = Grid(cargs.x, cargs.y, cargs.c)
        city = g.random_city()

        if cargs.static_method:
            player = Player(city.r, city.c, g, nearest_city)
        else:
            player = Player(city.r, city.c, g, learn)

        total_reward = 0
        total_move = 0

        if cargs.static_method:
            while not g.solved():
                old_grid = deepcopy(g)
                reward, action = player.move_strat(cargs)
                total_move += 1
                total_reward += reward
                if cargs.verbose:
                    print('{} cities remaining'.format(len(g.cities)))
                    print(g)
                    sleep(.5)
        else:
            while not player.grid.solved():
                r = learn(player, cargs)
                total_reward += r
                total_move += 1
                if cargs.verbose:
                    print(str(player.grid) + '\n')
                    sleep(.5)

        if cargs.verbose:
            print('WIN')
            print(total_move)
            print(total_reward)

        total_rewards.append(total_reward)
        total_moves.append(total_move)
        if i % 100 == 0 and i > 1:
            print(Output(total_rewards, total_moves))
            total_rewards = []
            total_moves = []
        print('{} out of {}'.format(i, cargs.iters))
        sys.stdout.flush()

        i += 1
        if i > cargs.iters > 0:
            break
