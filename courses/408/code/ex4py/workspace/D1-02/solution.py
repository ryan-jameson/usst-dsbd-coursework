from __future__ import annotations

import sys


def solve() -> None:
    data = sys.stdin.read().strip().split()
    n = int(data[0])
    a = list(map(int, data[1:n + 1]))
    print(max(a), min(a))
    pass


if __name__ == "__main__":
    solve()
