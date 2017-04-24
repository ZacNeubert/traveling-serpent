#!/usr/bin/python3
import datetime
import json

import redis
import argparse
import sys

from copy import copy, deepcopy
from random import randint
from math import sqrt
from statistics import mean, stdev
from time import sleep

from learning import learn
from strategy import *
from moves import *
from prettyprint import *

parser = argparse.ArgumentParser()
parser.add_argument('--verbose', action='store_true')
parser.add_argument('--eps', type=float, action='store')
parser.add_argument('--iters', type=int, action='store', default=1000)
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
        else: #Out of bounds
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
    OBSERVED = 2
    CITY = 3
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
        return ''.join([''.join([str(j) for j in col]) for col in self.grid])


class Output:
    def __init__(self, total_rewards, total_moves):
        dt = datetime.datetime.now()
        self.time = dt.strftime('%Y%m%d %H:%M:%S.%f %z')
        self.timestamp = dt.timestamp()
        self.length = len(total_moves)
        self.mean_reward = mean(total_rewards)
        self.stdev_reward = stdev(total_rewards)
        self.min_reward = min(total_rewards)
        self.max_reward = max(total_rewards)
        self.mean_move = mean(total_moves)
        self.stdev_move = stdev(total_moves)
        self.min_move = min(total_moves)
        self.max_move = max(total_moves)

    def __str__(self):
        return json.dumps(self.__dict__)


if __name__ == '__main__':
    total_rewards = []
    total_moves = []
    i = 0
    while True:
        g = Grid(10, 10, 5)
        city = g.random_city()
        player = Player(city.r, city.c, g, learn)

        total_reward = 0
        total_move = 0
        while not player.grid.solved():
            r = learn(player, cargs)
            total_reward += r
            total_move += 1
            if cargs.verbose:
                print(str(player.grid) + '\n')

        if cargs.verbose:
            print('WIN')
            print(total_move)
            print(total_reward)

        total_rewards.append(total_reward)
        total_moves.append(total_move)
        if i % 1000 == 0 and i > 1:
            print(Output(total_rewards, total_moves))
            sys.stdout.flush()
            total_rewards = []
            total_moves = []

        # while not g.solved():
        #    old_grid = copy(g)
        #    reward, action = player.move_strat(cargs)
        #    if len(g.cities) < len(old_grid.cities):
        #        print(len(g.cities))
        #        reward += 50
        #    total_reward += reward
        #    if cargs.verbose:
        #        print('{} cities remaining'.format(len(g.cities)))
        #        sleep(.05)

        i += 1
        if i > cargs.iters > 0:
            break