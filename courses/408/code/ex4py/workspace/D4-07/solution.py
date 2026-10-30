from __future__ import annotations

import sys


def solve() -> None:
    data = sys.stdin.read().strip().split()
    # 在这里完成算法，并用 print 输出答案。
    n=int(data[0])
    intervals=[list(map(int,data[2*i+1:2*i+3])) for i in range(n)]
    intervals.sort(key=lambda x:x[1])
    ans=0
    end=-1
    for start,finish in intervals:
        if start>=end:
            ans+=1
            end=finish
    print(ans)
    pass


if __name__ == "__main__":
    solve()
