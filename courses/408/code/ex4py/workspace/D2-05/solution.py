from __future__ import annotations
from collections import deque
import sys


def solve() -> None:
    data = sys.stdin.read().strip().split()
    # 在这里完成算法，并用 print 输出答案。
    n=int(data[0])
    k=int(data[1])
    q=deque()
    ans=[]
    for i in range(k-1):
        q.append(int(data[i+2]))
    for i in range(n+1-k):
        q.append(int(data[i+1+k]))
        ans.append(max(q))
        q.popleft()
    print(*ans)
    pass


if __name__ == "__main__":
    solve()
