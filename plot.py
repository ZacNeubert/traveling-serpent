import json
import matplotlib.pyplot as plot
import argparse
from statistics import mean

parser = argparse.ArgumentParser()
parser.add_argument('--infiles', action='store', nargs='+')
parser.add_argument('--fields', action='store', nargs='+')
parser.add_argument('--x-field', action='store')
args = parser.parse_args()

def read_file(infile):
    with open(infile, 'r') as inf:
        file_json = sorted([json.loads(line) for line in inf.readlines()], key=lambda line: line[args.x_field])
        return file_json

if __name__ == '__main__':
    file_json_dicts = {file.split(':')[0]: read_file(file.split(':')[1]) for file in args.infiles}
    for field in args.fields:
        for file_title, file_content in file_json_dicts.items():
            times = [d[args.x_field] for d in file_content]
            values = [d[field] for d in file_content]

            mean_runs = mean([d['length'] for d in file_content])

            if not times:
                raise Exception('No x axis')
            if not values:
                raise Exception('No y axis')

            fig = plot.figure()
            x_label = input('What is {}? '.format(args.x_field))
            y_label = input('What is {}? '.format(field))

            x_label = x_label.replace('RUNS', str(int(mean_runs)))
            y_label = y_label.replace('RUNS', str(int(mean_runs)))

            plot.xlabel(x_label)
            plot.ylabel(y_label)
            fig.suptitle(file_title, fontsize=20)
            ax = fig.add_subplot(111)
            ax.grid(True)
            ax.plot(times, values)
            plot.show()
