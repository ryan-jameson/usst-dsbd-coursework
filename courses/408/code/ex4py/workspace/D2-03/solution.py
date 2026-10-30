from __future__ import annotations

import sys


def solve() -> None:
    data = sys.stdin.read().strip().split()
    # 在这里完成算法，并用 print 输出答案。
    n=int(data[0])
    nums=list(map(int,data[1:n+1]))
    stack=[]
    ans=[-1]*len(nums)
    index=0
    for i in range(n):
        while stack and nums[stack[-1]]<nums[i]:
            index=stack.pop()
            ans[index]=nums[i]
        stack.append(i)
    print(*ans)
    pass


if __name__ == "__main__":
    solve()
