from __future__ import annotations

import sys


def solve() -> None:
    data = sys.stdin.read().strip().split()
    # 在这里完成算法，并用 print 输出答案。
    n=int(data[0])
    W=int(data[1])
    items=[list(map(int,data[2*(i+1):2*(i+2)])) for i in range(n)]
    dp=[0]*(W+1)
    for w,v in items:
        for i in range(W,w-1,-1):
            dp[i]=max(dp[i],dp[i-w]+v)
    print(dp[W])
        
    pass


if __name__ == "__main__":
    solve()
