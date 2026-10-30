from __future__ import annotations

import sys

def solve() -> None:
    data = sys.stdin.read().strip().split()
    # 在这里完成算法，并用 print 输出答案。
    n=int(data[0])
    m=int(data[1])
    grid=[]
    count=0
    for i in range(n):
        grid.append(list(data[i+2]))
        
    def dfs(i,j):
        dirs=[(1,0),(-1,0),(0,1),(0,-1)]
        if i<0 or i>=n or j<0  or j>=m:
            return
        if grid[i][j]=='0':
            return
        else:
            grid[i][j]='0'
            for (dx,dy) in dirs:
                dfs(i+dx,j+dy)
    
    for i in range(n):
        for j in range(m):
            if grid[i][j]=='1':
                count+=1
                dfs(i,j)
    print(count)
    pass


if __name__ == "__main__":
    solve()
