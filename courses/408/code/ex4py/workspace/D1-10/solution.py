from __future__ import annotations

import sys


def solve() -> None:
    data = sys.stdin.read().strip().split()
    # 在这里完成算法，并用 print 输出答案。
    s=''
    s=data[0]
    ans=''
    count=1
    for i in range(1,len(s)):
       if s[i]==s[i-1]:
           count+=1
       else:
           ans+=s[i-1]+str(count)
           count=1
    ans+=s[-1]+str(count)
    print(ans)
           
    pass


if __name__ == "__main__":
    solve()
