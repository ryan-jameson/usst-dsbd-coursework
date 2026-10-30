from __future__ import annotations

import sys


def solve() -> None:
    data = sys.stdin.read().strip().split()
    # 在这里完成算法，并用 print 输出答案。
    n=int(data[0])
    intervals=[list(map(int,data[2*i+1:2*i+3])) for i in range(n)]
    intervals.sort(key=lambda x:x[0])
    start,finish=intervals[0]
    for i in range(1,n):
        next_start,next_finish=intervals[i]
        if next_start <= finish:
            if next_finish > finish:
                finish=next_finish
        else:
            print(start,finish)
            start,finish=next_start,next_finish
    print(start,finish)
    pass


if __name__ == "__main__":
    solve()
