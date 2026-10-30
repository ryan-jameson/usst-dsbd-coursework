from __future__ import annotations

import sys


def solve() -> None:
    data = sys.stdin.read().strip().split()
    # 在这里完成算法，并用 print 输出答案。
    a=int(data[0])
    b=int(data[1])
    ans=1
    while b!=0:
        ans=b
        a,b=b,a%b
    print(ans)
    pass


if __name__ == "__main__":
    solve()
