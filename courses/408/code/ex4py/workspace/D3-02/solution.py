from __future__ import annotations

import sys


def solve() -> None:
    data = sys.stdin.read().strip().split()
    # 在这里完成算法，并用 print 输出答案。
    n=int(data[0])
    nums=list(map(int,data[1:n+1]))
    left=0
    ans=[]
    for right in range(1,n):
        if nums[left]==nums[right]:
            continue
        else:
            ans.append(nums[left])  
            left=right
    ans.append(nums[left])
    print(len(ans))
    print(*ans) 
    pass


if __name__ == "__main__":
    solve()
