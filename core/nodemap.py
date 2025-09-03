### Responsável por transformar nomes de nós em índices numéricos ###

import re

class NodeMap:
    def __init__(self):
        self.map = {"0": 0, "GND": 0, "gnd": 0}
        self.rev = {0: "0"}
        self.next_idx = 1

    def get(self, label):
        if label in self.map:
            return self.map[label]
        if re.fullmatch(r"-?\d+", label):
            val = int(label)
            if val == 0: return 0
            if val not in self.rev:
                self.map[label] = val
                self.rev[val] = label
                self.next_idx = max(self.next_idx, val + 1)
            return val
        idx = self.next_idx
        self.map[label] = idx
        self.rev[idx] = label
        self.next_idx += 1
        return idx

    @property
    def count(self):
        return max(self.rev.keys()) + 1
