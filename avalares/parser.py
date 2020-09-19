import heapq
import re
from collections import namedtuple
from typing import List, Tuple

from avalares.pattern_detector import PatternDetector, PatternMarking

token_matchers = [
    r'(?:{})'.format('|'.join([
        r'(?P<string>[a-zA-Z_][a-zA-Z_0-9&=/]*)',
        r'(?P<float>[0-9]+\.[0-9]+)',
        r'(?P<int>[0-9]+)',
        r'(?P<space> +)'
    ])),
    r'(?:{})'.format('|'.join([
        r'(?P<string>[a-zA-Z_][a-zA-Z_0-9&=/]*)',
        r'(?P<float>[0-9]+\.[0-9]+|[0-9]+)',
        r'(?P<space> +)'
    ]))
]

value_types = {
    'string', 'float', 'int'
}

converters = {
    'string': lambda x: x,
    'float': float,
    'int': int
}

ParseResult = namedtuple('ParseResult', 'rows labels types')
TokenData = namedtuple('TokenData', 'labels values')


def parse(text: str, convert_values=True) -> ParseResult:
    text = text.replace('\r\n', '\n').strip()
    best_result = None
    for token_matcher in token_matchers:
        result, amount_used = _parse_tokens(_tokenize_string(text, token_matcher), convert_values)
        if not best_result or len(best_result.rows) < len(result.rows):
            best_result = result
        if amount_used > 0.8:
            break
    return best_result


def _parse_tokens(data: List[str], convert_values=True) -> (ParseResult, int):
    detector = PatternDetector()
    for width in range(2, len(data.labels) + 1):
        for i in range(width, len(data.labels) + 2, width):
            vals = data.labels[i - width:i]
            if len(vals) < width:
                prev = data.labels[i - 2 * width:i - width]
                vals.extend(prev[len(vals):])
            detector.mark_pattern(vals, i - width)
        detector.finish()
    
    if not detector.pattern_counts:
        return ParseResult([], [], []), 1.0

    score = lambda x: x.count ** 2 * len(x.pattern)
    marking = heapq.nlargest(1, detector.pattern_counts, key=score)[0]

    delim = _detect_delimiter(data.labels[marking.start_pos:], marking.pattern)
    data_start, schema = _fix_offset(data, marking, delim)
    rows = _extract_rows(data, data_start, schema, delim, convert_values)
    label_names = _try_extract_header(data, data_start, delim, schema)
    types = [i for i in schema if i in value_types]
    return ParseResult(rows, label_names, types), 1 - data_start / (len(data) - 1)


def _extract_rows(data: TokenData, pos: int, schema: tuple, delim: str, convert_values=True):
    rows = []
    while data.labels[pos:pos + len(schema)] == schema:
        labels = data.labels[pos:pos + len(schema)]
        values = data.values[pos:pos + len(schema)]
        rows.append(tuple(
            converters[label](value) if convert_values else value
            for label, value in zip(labels, values)
            if label in value_types
        ))
        pos += len(schema)
        if pos >= len(data.labels) or data.labels[pos] != delim:
            break
        pos += 1
    return rows


def _fix_offset(data: TokenData, marking: PatternMarking, delim: str) -> Tuple[int, tuple]:
    pattern = marking.pattern
    if delim not in pattern:
        return marking.start_pos, pattern
    delim_pos = pattern.index(delim)
    schema = pattern[delim_pos + 1:] + pattern[:delim_pos]
    pos = marking.start_pos - len(pattern[delim_pos + 1:])
    if data.labels[pos:pos + len(schema)] != schema:
        pos += len(schema) + 1
    data_start = pos
    return data_start, schema


def _detect_delimiter(data_labels: list, pattern: tuple) -> str:
    chars = set(data_labels) - value_types
    last_char = {c: -1 for c in chars}
    detectors = {c: PatternDetector() for c in chars}
    for i, c in enumerate(data_labels):
        if c in value_types:
            continue
        dist = i - last_char[c]
        detectors[c].mark_pattern(dist, last_char[c])
        last_char[c] = i
    for c, last_i in last_char.items():
        dist = len(data_labels) - last_i
        detectors[c].mark_pattern(dist, len(data_labels))
        detectors[c].finish()

    return max(detectors, key=lambda x: max(
        (count ** 2 * interval if interval >= len(pattern) else 0, x)
        for count, start_pos, interval in detectors[x].pattern_counts
    ))


def _tokenize_string(text: str, token_matcher: str) -> TokenData:
    token_labels = []
    token_values = []
    next_char = 0
    for match in re.finditer(token_matcher, text):
        a, b = match.span()
        if a > next_char:
            token_labels.extend(text[next_char:a])
            token_values.extend(text[next_char:a])
        label, value = next(iter(((k, v) for k, v in match.groupdict().items() if v is not None)))
        token_labels.append(label)
        token_values.append(value)
        next_char = b
    a = len(text)
    if a > next_char:
        token_labels.extend(text[next_char:a])
        token_values.extend(text[next_char:a])
    return TokenData(token_labels, token_values)


def _step_back_line(tokens: TokenData, pos: int, delim: str):
    end_pos = pos - 1
    pos = pos - 2
    while pos >= 0 and tokens.labels[pos] != delim:
        pos -= 1
    pos += 1
    return pos, end_pos


def _try_extract_header(tokens: TokenData, data_start: int, delim: str, schema: tuple) -> List[str]:
    label_names = []
    pos, end_pos = _step_back_line(tokens, data_start, delim)
    while pos >= 0:
        num_schema_vals = sum(i in value_types for i in schema)
        num_label_vals = sum(i in value_types for i in tokens.labels[pos:end_pos])
        if num_label_vals == 0:
            pos, end_pos = _step_back_line(tokens, pos, delim)
            continue
        if num_schema_vals == num_label_vals:
            for token, value in zip(tokens.labels[pos:end_pos], tokens.values[pos:end_pos]):
                if token in value_types:
                    label_names.append(value)
        break
    return label_names
