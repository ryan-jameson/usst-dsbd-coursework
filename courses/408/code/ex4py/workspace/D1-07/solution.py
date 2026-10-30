from __future__ import annotations

import sys


def solve() -> None:
    data = sys.stdin.read().strip().split()
    # 在这里完成算法，并用 print 输出答案。
    n = int(data[0])
    students =[]
    index =1
    for i in range(n):
        name=data[index]
        score=int(data[index+1])
        students.append((name,score))
        index+=2
    students.sort(key=lambda x:(-x[1],x[0]))
    for name,score in students:
        print(name,score)
        
    pass


if __name__ == "__main__":
    solve()
