from __future__ import annotations

import sys


def solve() -> None:
    data = sys.stdin.read().strip()
    # 在这里完成算法，并用 print 输出答案。
    pairs={
        ')':'(',
        ']':'[',
        '}':'{'
    }
    stack=[]
    flag=False
    for c in data:
        if c in '([{':
            stack.append(c)
        elif stack[-1]==pairs[c]:
            stack.pop()
            flag=True
    if flag and len(stack)==0:
        print("YES")
    else:
        print("NO")
    pass


if __name__ == "__main__":
    solve()
