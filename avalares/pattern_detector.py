from collections import namedtuple

from typing import List

PatternMarking = namedtuple('PatternMarking', 'count start_pos pattern')

PatternMarking.__repr__ = lambda x: '({}, {}, {})'.format(x.count, x.start_pos, x.pattern)


class PatternDetector:
    def __init__(self):
        self.last_pattern = None
        self.count = 0
        self.start_pos = None
        self.pattern_counts = []  # type: List[PatternMarking]
    
    def __repr__(self):
        return 'PatternDetector({})'.format(', '.join('{}={}'.format(k, v) for k, v in vars(self).items()))

    def mark_pattern(self, pattern, start_pos):
        if pattern != self.last_pattern:
            self.finish()
            self.count = 1
            self.start_pos = start_pos
            self.last_pattern = pattern
        else:
            self.count += 1

    def finish(self):
        if self.last_pattern is not None:
            self.pattern_counts.append(PatternMarking(self.count, self.start_pos, self.last_pattern))
            self.last_pattern = None
            self.count = 0
            self.start_pos = None
