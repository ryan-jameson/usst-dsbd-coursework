from __future__ import annotations

import sys


def solve() -> None:
    data = sys.stdin.read().strip().split()
    # 在这里完成算法，并用 print 输出答案。
    n=int(data[0])
    nums=list(map(int,data[1:n+1]))
    counts=[]
    count=1
    for i in range(1,n):
        if nums[i]==nums[i-1]+1:
            count+=1
        else:
            counts.append(count)
            count=1
    print(max(counts))
    pass


if __name__ == "__main__":
    solve()
