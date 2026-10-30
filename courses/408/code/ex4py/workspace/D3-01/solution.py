from __future__ import annotations

import sys


def solve() -> None:
    data = sys.stdin.read().strip().split()
    # 在这里完成算法，并用 print 输出答案。
    n=int(data[0])
    target=int(data[1])
    nums=list(map(int,data[2:n+2]))
    left=0
    right=len(nums)-1
    while left<right:
        ans=nums[left]+nums[right]
        if ans == target:
            print(nums[left],nums[right])
            break
        elif ans<target:
            left+=1
        else:
            right-=1
    pass


if __name__ == "__main__":
    solve()
