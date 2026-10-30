from __future__ import annotations

import sys


def solve() -> None:
    data = sys.stdin.read().strip().split()
    # 在这里完成算法，并用 print 输出答案。
    n=int(data[0])
    nums=list(map(int,data[1:]))
    nums=nums[::-1]
    path=[]
    def dfs(i):
        if i==n:
            if len(path)==0:
                print("EMPTY")
            else:
                print(*sorted(path))
            return
        #不选当前元素
        dfs(i+1)
        
        #选当前元素
        path.append(nums[i])
        dfs(i+1)
        
        path.pop()
    dfs(0)
    pass


if __name__ == "__main__":
    solve()
