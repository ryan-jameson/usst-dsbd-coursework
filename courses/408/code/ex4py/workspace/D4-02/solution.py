from __future__ import annotations

import sys


def solve() -> None:
    data = sys.stdin.read().strip().split()
    # 在这里完成算法，并用 print 输出答案。
    n=int(data[0])
    cost=list(map(int,data[1:]))
    cost+=[0]
    dp=[0]*(n+1)
    dp[0]=cost[0]
    dp[1]=cost[1]
    for i in range(2,n+1):
        dp[i]=min(dp[i-1],dp[i-2])+cost[i]
    print(dp[n])
    pass


if __name__ == "__main__":
    solve()
