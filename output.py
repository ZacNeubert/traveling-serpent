import datetime
import json
from statistics import mean, stdev


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