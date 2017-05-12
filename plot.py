import json
import matplotlib.pyplot as plot
import argparse
from statistics import mean

parser = argparse.ArgumentParser()
parser.add_argument('--infiles', action='store', nargs='+')
parser.add_argument('--fields', action='store', nargs='+')
parser.add_argument('--x-field', action='store')
parser.add_argument('--start-i', action='store', type=int, default=0)
parser.add_argument('--end-i', action='store', type=int, default=9999999)
args = parser.parse_args()

KNOWN_NAMES = {
    'timestamp': 'Timestamp (seconds)',
    'mean_move': 'Mean Moves over RUNS Runs',
    'mean_reward': 'Mean Reward over RUNS Runs',
    'stdev_move': 'Standard Deviation of Move Count over RUNS Runs',
    'stdev_reward': 'Standard Deviation of Reward over RUNS Runs',
}

def read_file(infile):
    with open(infile, 'r') as inf:
        file_json = sorted([json.loads(line) for line in inf.readlines() if 'mean' in line], key=lambda line: line[args.x_field])
        return file_json

def translate_label(label, mean_runs):
    if KNOWN_NAMES.get(label):
        label = KNOWN_NAMES.get(label)
    else: 
        label = input('What is {}? '.format(label))
    label = label.replace('RUNS', str(int(mean_runs)))
    return label


if __name__ == '__main__':
    file_json_dicts = {file.split(':')[0]: read_file(file.split(':')[1]) for file in args.infiles}
    for field in args.fields:
        for file_title, file_content in file_json_dicts.items():
            times = [d[args.x_field] for d in file_content][args.start_i:args.end_i]
            values = [d[field] for d in file_content][args.start_i:args.end_i]

            mean_runs = mean([d['length'] for d in file_content][args.start_i:args.end_i])
            mean_vals = mean(values)
            print(mean(values))

            if not times:
                raise Exception('No x axis')
            if not values:
                raise Exception('No y axis')

            fig = plot.figure()

            x_label = translate_label(args.x_field, mean_runs)
            y_label = translate_label(field, mean_runs)

            plot.xlabel(x_label)
            plot.ylabel(y_label)
            fig.suptitle(file_title, fontsize=20)
            ax = fig.add_subplot(111)
            ax.grid(True)
            ax.plot(times, values)
            plot.show()
