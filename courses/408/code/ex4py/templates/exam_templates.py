"""机试模板库：训练时理解并手写，考试时按题意裁剪。"""

from __future__ import annotations

from bisect import bisect_left
from collections import deque
from collections.abc import Iterable


def fast_read(raw: str) -> list[int]:
    """对应 sys.stdin.buffer.read().split() 的可测试版本。"""
    return list(map(int, raw.split()))


def lower_bound(a: list[int], target: int) -> int:
    """返回第一个 >= target 的下标；不存在则返回 len(a)。"""
    left, right = 0, len(a)
    while left < right:
        middle = (left + right) // 2
        if a[middle] < target:
            left = middle + 1
        else:
            right = middle
    return left


def bfs_grid(grid: list[str], start: tuple[int, int]) -> list[list[int]]:
    """# 为障碍，返回 start 到每格的最短步数。"""
    rows, cols = len(grid), len(grid[0])
    distance = [[-1] * cols for _ in range(rows)]
    sx, sy = start
    distance[sx][sy] = 0
    queue = deque([start])
    while queue:
        x, y = queue.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < rows and 0 <= ny < cols and grid[nx][ny] != "#" and distance[nx][ny] == -1:
                distance[nx][ny] = distance[x][y] + 1
                queue.append((nx, ny))
    return distance


def dfs_grid(grid: list[str], start: tuple[int, int]) -> set[tuple[int, int]]:
    """迭代 DFS，避免大网格递归深度风险。"""
    rows, cols = len(grid), len(grid[0])
    seen: set[tuple[int, int]] = set()
    stack = [start]
    while stack:
        x, y = stack.pop()
        if (x, y) in seen or not (0 <= x < rows and 0 <= y < cols) or grid[x][y] == "#":
            continue
        seen.add((x, y))
        stack.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))
    return seen


class UnionFind:
    def __init__(self, size: int) -> None:
        self.parent = list(range(size))
        self.component_size = [1] * size
        self.components = size

    def find(self, x: int) -> int:
        while x != self.parent[x]:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a: int, b: int) -> bool:
        root_a, root_b = self.find(a), self.find(b)
        if root_a == root_b:
            return False
        if self.component_size[root_a] < self.component_size[root_b]:
            root_a, root_b = root_b, root_a
        self.parent[root_b] = root_a
        self.component_size[root_a] += self.component_size[root_b]
        self.components -= 1
        return True


def prefix_sums(values: Iterable[int]) -> list[int]:
    result = [0]
    for value in values:
        result.append(result[-1] + value)
    return result


def difference_updates(size: int, updates: Iterable[tuple[int, int, int]]) -> list[int]:
    """对 0-based 闭区间 [left, right] 批量加 delta。"""
    difference = [0] * (size + 1)
    for left, right, delta in updates:
        difference[left] += delta
        if right + 1 < size:
            difference[right + 1] -= delta
    result: list[int] = []
    current = 0
    for index in range(size):
        current += difference[index]
        result.append(current)
    return result


def zero_one_knapsack(items: Iterable[tuple[int, int]], capacity: int) -> int:
    dp = [0] * (capacity + 1)
    for weight, value in items:
        for current in range(capacity, weight - 1, -1):
            dp[current] = max(dp[current], dp[current - weight] + value)
    return dp[capacity]


def lis_length(values: Iterable[int]) -> int:
    tails: list[int] = []
    for value in values:
        index = bisect_left(tails, value)
        if index == len(tails):
            tails.append(value)
        else:
            tails[index] = value
    return len(tails)
