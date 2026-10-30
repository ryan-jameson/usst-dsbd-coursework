from __future__ import annotations

import sys


def solve() -> None:
    data = sys.stdin.read().strip().split()
    # 在这里完成算法，并用 print 输出答案。
    n=int(data[0])
    nums=list(map(int,data[1:]))
    path=[]
    used=[False]*n
    def dfs():
        if len(path)==n:
            print(*path)
            return
        for i in range(n):
            if used[i]:
                continue#代表已经选过
            
            #没选过则添加
            path.append(nums[i])
            used[i]=True
            
            dfs()
            #撤销选过的数字
            path.pop()
            used[i]=False
    dfs()

    pass


if __name__ == "__main__":
    solve()
