from __future__ import annotations

import sys

import bisect
def solve() -> None:
    data = sys.stdin.read().strip().split()
    # 在这里完成算法，并用 print 输出答案。
    n=int(data[0])
    nums=list(map(int,data[1:]))
    tails=[]
    loc=0
    for i in range(n):
        loc=bisect.bisect_left(tails,nums[i])
        if loc==len(tails):
            tails.append(nums[i])
        else:
            tails[loc]=nums[i]
    print(len(tails))
    pass


if __name__ == "__main__":
    solve()
