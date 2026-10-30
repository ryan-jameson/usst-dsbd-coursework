from __future__ import annotations

import sys


def solve() -> None:
    data = sys.stdin.read().strip().split()
    # 在这里完成算法，并用 print 输出答案。
    stack=[]
    for c in data:
        if c.isdigit():
            stack.append(int(c))
        else :
            a=stack.pop()
            b=stack.pop()
            if c=='+':
                stack.append(a+b)
            if c=='-':
                stack.append(b-a)
            if c=='*':
                stack.append(a*b)
    print(stack[0])
    pass


if __name__ == "__main__":
    solve()
