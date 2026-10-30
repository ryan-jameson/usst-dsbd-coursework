from __future__ import annotations

import sys


def solve() -> None:
    data = sys.stdin.read().strip().split()
    # 在这里完成算法，并用 print 输出答案。
    x=int(data[0])
    ans=0
    left=0
    right=x
    while left<=right:
        mid=(left+right)//2
        if mid**2 <= x:
            ans=mid
            left=mid+1
        else:
            right=mid-1
    print(ans)
    pass


if __name__ == "__main__":
    solve()
