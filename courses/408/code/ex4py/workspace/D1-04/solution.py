from __future__ import annotations

import sys


def solve() -> None:
    data = sys.stdin.read().strip().split()
    # 在这里完成算法，并用 print 输出答案。
    n = int(data[0])
    nums= list(map(int, data[1:n + 1]))
    ans = []
    seen = set()
    for num in nums:
        if num not in seen:
            ans.append(num)
            seen.add(num)
    print(*ans)
    pass


if __name__ == "__main__":
    solve()
