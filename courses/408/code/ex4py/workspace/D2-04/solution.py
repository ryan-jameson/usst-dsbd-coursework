from __future__ import annotations
from collections import deque
import sys


def solve() -> None:
    data = sys.stdin.read().strip().split('\n')
    # 在这里完成算法，并用 print 输出答案。
    q=deque()
    for cmd in data[1:]:
        arr=cmd.split()
        if arr[0]=='PUSH':
            q.append(int(arr[1]))
        elif arr[0]=='FRONT':
            if len(q)==0:
                print("EMPTY")
            else:
                print(q[0])
        elif arr[0]=='POP':
            if len(q)==0:
                print("EMPTY")
            else:
                print(q.pop())
    pass


if __name__ == "__main__":
    solve()
