from __future__ import annotations

import sys


def solve() -> None:
    data = sys.stdin.read().strip().split()
    # 在这里完成算法，并用 print 输出答案。
    n = int(data[0])
    x = list(map(int,data[1:n+1]))
    t = int(data[n+1])
    print(x.count(t))
    pass


if __name__ == "__main__":
    solve()
