from __future__ import annotations

import sys


def solve() -> None:
    data = sys.stdin.read().strip().split()
    # 在这里完成算法，并用 print 输出答案。
    n=int(data[0])
    target=int(data[1])
    nums=list(map(int,data[2:n+2]))
    path=[]
    nums.sort()
    ans=0
    def dfs(i):
        nonlocal ans
        if i==n:
            return
        else:
            path.append(nums[i])
            if sum(path)==target:
                ans+=1
                path.pop()
                return
            elif sum(path) > target:
                path.pop()
                return
            else:
                for j in range(i+1,n):
                    dfs(j)
            path.pop()
            
    for i in range(n):
        dfs(i)
    print(ans)
    pass


if __name__ == "__main__":
    solve()
