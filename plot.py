import json

import matplotlib.pyplot as plot
import sys

if __name__ == '__main__':
    dicts = []
    i = 0
    while True:
        try:
            inp = input()
            print(inp)
            sys.stdout.flush()
            line = json.loads(inp)
        except Exception as e:
            print('Exception occurred {}'.format(e))
            pass
        dicts.append(line)
        dicts = sorted(dicts, key=lambda d: d['timestamp'])
        times = [d['timestamp'] for d in dicts]
        scores = [d['mean_reward'] for d in dicts]

        i += 1
        print(i)
        if i % 10 == 0:
            fig = plot.figure()
            ax = fig.add_subplot(111)
            ax.grid(True)
            ax.plot(times, scores)
            plot.show()
