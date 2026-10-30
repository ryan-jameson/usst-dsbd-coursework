from __future__ import annotations
from collections import deque
import sys

def solve() -> None:
    data = sys.stdin.read().strip().split()
    # 在这里完成算法，并用 print 输出答案。
    n=int(data[0])
    for i in range(1,n+1):
        if data[i]!='#':
            print(int(data[i]),end=' ')
    pass


if __name__ == "__main__":
    solve()
