import csv
import json
from os.path import isfile, splitext
from urllib import request

from avalares.parser import parse


def to_numpy(param):
    import numpy as np
    if param.startswith('http'):
        text = request.urlopen(param).read().decode()
    elif len(param) < 256 and isfile(param):
        _, ext = splitext(param)
        if ext == '.csv':
            with open(param, newline='') as csvfile:
                dialect = csv.Sniffer().sniff(csvfile.read(1024))
                csvfile.seek(0)
                reader = csv.reader(csvfile, dialect)
                return np.array(reader)
        elif ext == '.json':
            with open(param) as f:
                rows = json.load(f)
            if not isinstance(rows, list):
                raise ValueError('Cannot convert given json to numpy array')
            if rows and isinstance(rows[0], dict):
                labels = sorted(rows[0])
                return np.array([tuple(labels)] + [
                    tuple(row.get(k) for k in labels)
                    for row in rows
                ])
            else:
                return np.array(rows)
        else:
            with open(param) as f:
                text = f.read()
    else:
        text = param
    result = parse(text)
    return np.array(result.rows)


def to_pandas(param):
    import pandas as pd
    if param.startswith('http'):
        text = request.urlopen(param).read().decode()
    elif len(param) < 256 and isfile(param):
        _, ext = splitext(param)
        if ext == '.csv':
            return pd.read_csv(param)
        elif ext == '.json':
            return pd.read_json(param)
        else:
            with open(param) as f:
                text = f.read()
    else:
        text = param
    result = parse(text)
    return pd.DataFrame(result.rows, columns=result.labels or None)
