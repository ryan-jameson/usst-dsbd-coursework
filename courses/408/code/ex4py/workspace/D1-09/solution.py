from __future__ import annotations

import sys


def solve() -> None:
    data = sys.stdin.read().strip().split()
    # 在这里完成算法，并用 print 输出答案。
    n=int(data[0])
    main=0
    sub=0
    index=1
    for i in range(n):
        main+=int(data[index])
        sub+=int(data[(i+1)*n-i])
        index+=n+1
    print(main,sub)
    pass


if __name__ == "__main__":
    solve()
