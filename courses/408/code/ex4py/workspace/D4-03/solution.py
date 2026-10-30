from __future__ import annotations

import sys


def solve() -> None:
    data = sys.stdin.read().strip().split()
    # 在这里完成算法，并用 print 输出答案。
    n=int(data[0])
    amount=int(data[1])
    nums=list(map(int,data[2:n+2]))
    dp=[-1]*(amount+1)
    for i in nums:
        dp[i]=1
    
    for i in range(1,amount+1):
        for j in nums:
            if i-j>0 and dp[i-j]!=-1:
                if dp[i]==-1:
                    dp[i]=dp[i-j]+1
                else: dp[i]=min(dp[i],dp[i-j]+1)

    print(dp[amount])
    pass


if __name__ == "__main__":
    solve()
