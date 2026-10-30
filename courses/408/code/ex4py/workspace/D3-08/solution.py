from __future__ import annotations
from collections import deque
import sys


def solve() -> None:
    data = sys.stdin.read().strip().split()
    # 在这里完成算法，并用 print 输出答案。
    n=int(data[0])
    m=int(data[1])
    map=[]
    dirs=[(-1,0),(1,0),(0,1),(0,-1)]
    ans=0
    for i in range(n):
        map.append(list(data[i+2]))
    
    def bfs(i,j,step):
        q=deque([(i,j,step)])
        while q:
            x,y,step=q.popleft() 
            for dx,dy in dirs:
                nx=x+dx
                ny=y+dy
                if 0<=nx<n and 0<=ny<m :
                    if map[nx][ny]=='.':
                        map[nx][ny]='#'
                        q.append((nx,ny,step+1))
                    elif map[nx][ny]=='T':
                        return step+1
        
        return -1
    
    for i in range(n):
        for j in range(m):
            if map[i][j]=='S':
                map[i][j]='#'
                ans=bfs(i,j,0)
    print(ans)
    
            
    pass


if __name__ == "__main__":
    solve()
