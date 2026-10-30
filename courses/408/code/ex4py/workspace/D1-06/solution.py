from __future__ import annotations

import sys


def solve() -> None:
    data = sys.stdin.read().strip().split()
    # 在这里完成算法，并用 print 输出答案。
    a=0
    b=0
    c=0
    d=0
    for word in data:
        for char in word:
            if char.isalpha():
                a+=1
            elif char.isdigit():
                b+=1
            else:
                d+=1
    c=len(data)-1
    print(a,b,c,d)
    pass


if __name__ == "__main__":
    solve()
