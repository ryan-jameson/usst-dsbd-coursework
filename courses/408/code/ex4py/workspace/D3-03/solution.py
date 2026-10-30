from __future__ import annotations

import sys


def solve() -> None:
    data = sys.stdin.read().strip().split()
    # 在这里完成算法，并用 print 输出答案。
    n=int(data[0])
    target=int(data[1])
    nums=list(map(int,data[2:n+2]))
    left=0
    right=n-1
    ans=-1
    while left<=right:
        mid = (left+right)//2
        if nums[mid]==target:
            ans=mid
            right=mid-1
        elif nums[mid]>target:
            right=mid-1
        else: left=mid+1
    print(ans)
    pass


if __name__ == "__main__":
    solve()
