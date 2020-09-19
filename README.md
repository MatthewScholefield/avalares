# Avalares

*Automatic text data extraction tool*

Tool to automatically extract a pandas dataframe or numpy array out of a string of text.

Often times we want to quickly extract data from some dataset [like this](https://www1.udel.edu/htr/Statistics/Data/smokingcancer.txt),
but the dataset isn't in a standard form. It's very clear to a human what
parts of the text represent the data, and we could easily copy and paste
part of the text, writing some simple parser by splitting on a delimiter,
etc., but this project aims to automate that process.

## Usage

Via command line:

```bash
url=https://www1.udel.edu/htr/Statistics/Data/smokingcancer.txt
curl $url | avalares
curl $url | avalares -t json | jq '.[] | .LEUK'  # Gets LEUK row from data
curl $url | avalares -t json | jq '[.[] | .LUNG] | add / length'  # Gets average of LUNG row
curl $url > data.txt
avalares data.txt -o data.csv  # .csv, .json, .pkl, or .npy
```

Via python API:

```python
from avalares import to_pandas, to_numpy, parse
df = to_pandas('https://www1.udel.edu/htr/Statistics/Data/smokingcancer.txt')
df = to_pandas('data.txt')
data = to_numpy('1 2 3;4 5 6')

result = parse('Letter Number;a 1;b 2;c 3;d 4')
print(result.labels)  # ['Letter', 'Number']
print(result.types)  # ['string', 'int']
print(result.rows)  # [('a', 1), ('b', 2), ('c', 3), ('d', 4)]
```

## Installation

Install via `pip3`:

```bash
pip3 install --user avalares
```
