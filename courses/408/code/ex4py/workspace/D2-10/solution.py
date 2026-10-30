from __future__ import annotations
from collections import deque
import sys
class Treenode:
    def __init__(self,val):
        self.val=val
        self.left=None
        self.right=None
        pass

def solve() -> None:
    data = sys.stdin.read().strip().split()
    # 在这里完成算法，并用 print 输出答案。
    n=int(data[0])
    i=2
    flag=True
    root=Treenode(int(data[1]))
    q=deque([root])
    while i<=n:
        node=q.popleft()
        if data[i]!='#':
            node.left=Treenode(int(data[i]))
            q.append(node.left)
        else:
            flag=False
            break
        i+=1
        if data[i]!='#':
            node.right=Treenode(int(data[i]))
            q.append(node.right)
        else:
            flag=False
            break
        i+=1
        if node.left.val+node.right.val!=2*node.val:
            flag=False
            break
    if flag:
        print("YES")
    else:
        print("NO")
    pass


if __name__ == "__main__":
    solve()
