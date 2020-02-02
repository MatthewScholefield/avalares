"""
Tool to automatically extract a pandas dataframe or numpy array out of a string of text
"""
import csv
import io
import json
import pickle
import sys
from argparse import ArgumentParser
from os.path import splitext

from avalares.parser import parse


def to_json(data, label_names=None):
    return [
        {label_name: value for label_name, value in zip(label_names, row)}
        if label_names else
        list(row)
        for row in data
    ]


def write_csv(out_file, data, label_names=None):
    writer = csv.writer(out_file)
    if label_names:
        writer.writerow(label_names)
    writer.writerows(data)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('input_file', nargs='?')
    parser.add_argument('-o', '--output', help='File to write to (.json, .csv, .pkl, or .npy)')
    parser.add_argument('-t', '--type', help='Output format (json or csv)', choices=['json', 'csv'], default='csv')
    parser.add_argument('-n', '--no-header', action='store_true', help='Ignore label header')
    args = parser.parse_args()

    if not args.input_file and sys.stdin.isatty():
        parser.error('Please provide an input file or pipe input from stdin')

    if args.output:
        _, ext = splitext(args.output)
        if ext not in ['.json', '.csv', '.pkl', '.npy']:
            parser.error('Unknown output extension: ' + ext)

    if args.input_file:
        with open(args.input_file) as f:
            input_string = f.read()
    else:
        input_string = sys.stdin.read()

    result = parse(input_string)

    if args.no_header:
        result.labels.clear()

    if args.output:
        _, ext = splitext(args.output)
        if ext == '.json':
            with open(args.output, 'w') as f:
                json.dump(to_json(result.rows, result.labels), f)
        elif ext == '.csv':
            with open(args.output, 'w', newline='') as f:
                write_csv(f, result.rows, result.labels)
        elif ext == '.pkl':
            if result.labels:
                result.rows.insert(0, result.labels)
            with open(args.output, 'wb') as f:
                pickle.dump(result.rows, f)
        elif ext == '.npy':
            import numpy as np
            with open(args.output, 'wb') as f:
                np.save(f, np.array(result.rows))
    else:
        if args.type == 'json':
            print(json.dumps(to_json(result.rows, result.labels), indent=4 if sys.stdout.isatty() else None))
        elif args.type == 'csv':
            s = io.StringIO()
            write_csv(s, result.rows, result.labels)
            print(s.getvalue().strip())


if __name__ == '__main__':
    main()
