from __future__ import annotations

import sys


def solve() -> None:
    data = sys.stdin.read().strip().split()
    # 在这里完成算法，并用 print 输出答案。
    n=int(data[0])
    target=int(data[1])
    nums=list(map(int,data[2:n+2]))
    hash={}
    for i in range(n):
        need = target - nums[i]
        if need in hash:
            print(hash[need]+1,i+1)
            break
        else:
            hash[nums[i]]=i
    pass


if __name__ == "__main__":
    solve()
