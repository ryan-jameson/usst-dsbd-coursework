from __future__ import annotations

import sys


def solve() -> None:
    data = sys.stdin.read().strip().split()
    # 在这里完成算法，并用 print 输出答案。
    s= ""
    for word in data:
        for c in word: 
            if c.isalnum():
                s+=c
    s=s.lower()
    if s == s[::-1]:
        print("YES")
    else:
        print("NO")
    pass


if __name__ == "__main__":
    solve()
