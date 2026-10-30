from __future__ import annotations

import sys


def solve() -> None:
    data = sys.stdin.read().strip().split()
    # 在这里完成算法，并用 print 输出答案。
    n=int(data[0])
    ans=[0]*n
    s=0
    diff=[0]*n
    q=int(data[1])
    for i in range(q):
        l=int(data[2+3*i])
        r=int(data[3+3*i])
        k=int(data[4+3*i])
        diff[l-1]+=k
        if r<n :diff[r]=-k
    for i in range(n):
        s+=diff[i]
        ans[i]=s
    print(*ans)
    pass


if __name__ == "__main__":
    solve()
