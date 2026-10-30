from __future__ import annotations

import sys


def solve() -> None:
    data = sys.stdin.read().strip().split()
    # 在这里完成算法，并用 print 输出答案。
    n=int(data[0])
    q=int(data[1])
    nums=list(map(int,data[2:n+2]))
    loc=list(map(int,data[n+2:n+2+2*q]))
    pre=[0]*(n+1)
    for i in range(n):
        pre[i+1]=pre[i]+nums[i]
    l=0
    r=0
    for i in range(q):
        l=loc[2*i]
        r=loc[2*i+1]
        print(pre[r]-pre[l-1])
    pass


if __name__ == "__main__":
    solve()
