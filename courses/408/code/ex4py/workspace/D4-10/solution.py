from __future__ import annotations

import sys


def solve() -> None:
    data = sys.stdin.read().strip().split()
    # 在这里完成算法，并用 print 输出答案。
    n=int(data[0])
    m=int(data[1])
    alpha=[list(data[i+2]) for i in range(n)]

    target=list(data[n+2])
    dirs=[(-1,0),(1,0),(0,1),(0,-1)]
    def dfs(i,j,step):
        if i<0 or i>=n or j<0 or j>=m:
            return False

        if alpha[i][j]!=target[step]:
            return False
        if step==len(target)-1:
            return True
        c=alpha[i][j]
        alpha[i][j]='#'

        for dx,dy in dirs:
            if dfs(i+dx,j+dy,step+1):
                alpha[i][j]=c
                return True

        alpha[i][j]=c

        return False
        
    if any(dfs(i,j,0) for i in range(n) for j in range(m)):
        print("YES")
    else:
        print("NO")
                
    pass


if __name__ == "__main__":
    solve()
