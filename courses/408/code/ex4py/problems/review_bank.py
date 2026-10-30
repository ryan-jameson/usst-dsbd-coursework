from __future__ import annotations

from trainer.models import Problem, TestCase


SKELETON = '''from __future__ import annotations

import sys


def solve() -> None:
    data = sys.stdin.buffer.read().split()
    # 先写出算法信号、状态或不变量，再完成代码。
    pass


if __name__ == "__main__":
    solve()
'''


REVIEW_GROUPS: dict[str, tuple[str, tuple[str, str]]] = {
    "basic": ("基础统计与字符串", ("R01", "R02")),
    "sort_hash": ("排序与哈希", ("R03", "R04")),
    "stack_queue": ("栈与单调结构", ("R05", "R06")),
    "pointer_binary": ("双指针与二分", ("R07", "R08")),
    "range": ("前缀和与差分", ("R09", "R10")),
    "grid": ("网格 DFS/BFS", ("R11", "R12")),
    "tree_graph": ("树与并查集", ("R13", "R14")),
    "shortest_order": ("拓扑与最短路", ("R15", "R16")),
    "search_greedy": ("回溯与贪心", ("R17", "R18")),
    "dp": ("动态规划", ("R19", "R20")),
}


def _case(raw: tuple[str, str], name: str) -> TestCase:
    stdin, expected = raw
    return TestCase(stdin=stdin.rstrip() + "\n", expected=expected.rstrip() + "\n", name=name)


def _triplet(
    prefix: str,
    day: int,
    difficulty: str,
    tags: tuple[str, ...],
    titles: tuple[str, str, str],
    statements: tuple[str, str, str],
    public: tuple[tuple[str, str], tuple[str, str], tuple[str, str]],
    hidden: tuple[tuple[str, str], tuple[str, str], tuple[str, str]],
    hints: tuple[str, str, str],
    solution: str,
    complexity: str,
    pitfalls: tuple[str, ...],
    input_format: str,
    output_format: str,
    constraints: str,
) -> tuple[Problem, ...]:
    return tuple(
        Problem(
            id=f"{prefix}-{index:02d}",
            day=day,
            title=titles[index - 1],
            difficulty=difficulty,
            tags=tags,
            statement=statements[index - 1],
            input_format=input_format,
            output_format=output_format,
            constraints=constraints,
            public_cases=(_case(public[index - 1], "公开样例"),),
            hidden_cases=(_case(hidden[index - 1], "隐藏边界"),),
            hints=hints,
            skeleton=SKELETON,
            reference_solution=solution.strip() + "\n",
            complexity=complexity,
            pitfalls=pitfalls,
        )
        for index in range(1, 4)
    )


REVIEW_PROBLEMS: tuple[Problem, ...] = sum(
    (
        _triplet(
            "R01", 1, "简单", ("统计", "数组", "输入输出"),
            ("训练数据概览", "温度记录摘要", "服务器负载汇总"),
            (
                "给出 n 个训练得分，输出总分、最高分和最低分。",
                "给出 n 个整数温度，输出总和、最高值和最低值。",
                "给出 n 次服务器负载整数，输出总负载、峰值和谷值。",
            ),
            (("5\n2 4 1 8 5", "20 8 1"), ("4\n-3 0 6 -1", "2 6 -3"), ("3\n7 7 7", "21 7 7")),
            (("1\n-9", "-9 -9 -9"), ("2\n10 -10", "0 10 -10"), ("5\n0 0 0 0 0", "0 0 0")),
            ("一次遍历可同时得到三项统计。", "总和初始为 0，最大最小应从首元素或内置函数得到。", "读取 a 后输出 sum(a)、max(a)、min(a)。"),
            """import sys\nd=list(map(int,sys.stdin.buffer.read().split())); a=d[1:1+d[0]]; print(sum(a),max(a),min(a))""",
            "O(n) 时间，O(n) 输入空间", ("全负数时最大值不能初始化为 0。", "n=1 时最大最小相同。"),
            "第一行 n，第二行 n 个整数。", "一行输出总和、最大值、最小值。", "1≤n≤200000，数值绝对值≤10^9。",
        ),
        _triplet(
            "R02", 1, "简单", ("字符串", "计数", "排序"),
            ("最高频字母", "DNA 主导碱基", "日志主报码"),
            (
                "输入一行小写字母，输出出现最多的字母及次数；并列取字典序小者。",
                "输入只含 A/C/G/T 的序列，输出最高频字符及次数；并列取字典序小者。",
                "输入一行由小写字母组成的日志码，输出最高频字符及次数；并列取字典序小者。",
            ),
            (("banana", "a 3"), ("ACGTAC", "A 2"), ("zzxyyx", "x 2")),
            (("c", "c 1"), ("TTGG", "G 2"), ("bbaa", "a 2")),
            ("需要频率统计与并列规则。", "Counter 后按 (-次数,字符) 排序。", "取 min(counter, key=lambda c: (-counter[c], c))。"),
            """from collections import Counter\ns=input().strip(); c=Counter(s); ch=min(c,key=lambda x:(-c[x],x)); print(ch,c[ch])""",
            "O(n+k) 时间，O(k) 空间", ("并列时不能依赖首次出现顺序。", "输入保证非空。"),
            "输入一行非空字符串。", "输出字符和出现次数，中间一个空格。", "字符串长度≤200000。",
        ),
        _triplet(
            "R03", 1, "简单", ("排序", "元组", "多关键字"),
            ("竞赛榜单", "任务优先榜", "候选人排序"),
            (
                "每条记录含姓名、得分、罚时；按得分降序、罚时升序、姓名升序输出姓名。",
                "每条记录含任务名、收益、耗时；按收益降序、耗时升序、名称升序输出名称。",
                "每条记录含候选人、票数、登记号；按票数降序、登记号升序、姓名升序输出姓名。",
            ),
            (("4\nLi 90 30\nAn 90 20\nBo 80 10\nWu 90 20", "An\nWu\nLi\nBo"), ("3\nA 5 9\nB 8 10\nC 8 2", "C\nB\nA"), ("3\nZ 10 2\nA 10 2\nB 11 8", "B\nA\nZ")),
            (("2\nb 1 1\na 1 1", "a\nb"), ("1\nonly 0 0", "only"), ("2\nX -1 2\nY -1 1", "Y\nX")),
            ("把排序规则按优先级写成元组。", "降序数值取负号，升序字段保持原值。", "records.sort(key=lambda x: (-x[1], x[2], x[0]))。"),
            """n=int(input()); a=[]\nfor _ in range(n):\n s,x,y=input().split(); a.append((s,int(x),int(y)))\na.sort(key=lambda z:(-z[1],z[2],z[0]))\nfor s,_,_ in a: print(s)""",
            "O(n log n) 时间，O(n) 空间", ("三项键的方向不同。", "不要用多次不稳定的手写交换。"),
            "第一行 n，随后 n 行为名称、主指标、次指标。", "按规则逐行输出名称。", "1≤n≤100000，名称无空格。",
        ),
        _triplet(
            "R04", 2, "中等", ("哈希", "计数", "两数之和"),
            ("目标和配对数", "互补功率组合", "预算搭档数量"),
            (
                "统计数组中满足 i<j 且 a[i]+a[j]=target 的下标对数量。",
                "统计两台设备功率之和等于目标值的不同下标对数量。",
                "统计两件商品价格之和恰等于预算的不同下标对数量。",
            ),
            (("5 6\n1 5 1 5 3", "4"), ("4 10\n4 6 5 5", "2"), ("6 8\n2 6 3 5 4 4", "3")),
            (("4 0\n0 0 0 0", "6"), ("3 5\n1 1 1", "0"), ("2 -3\n-1 -2", "1")),
            ("每到一个值 x，只与此前出现的 target-x 配对。", "字典保存已扫描值的出现次数。", "ans += freq[target-x]，然后 freq[x] += 1。"),
            """import sys\nfrom collections import defaultdict\nd=list(map(int,sys.stdin.buffer.read().split())); n,t=d[:2]; freq=defaultdict(int); ans=0\nfor x in d[2:2+n]: ans+=freq[t-x]; freq[x]+=1\nprint(ans)""",
            "O(n) 期望时间，O(n) 空间", ("重复值会产生多组下标对。", "必须先查询再记录当前元素。"),
            "第一行 n 和 target，第二行 n 个整数。", "输出满足条件的下标对数量。", "1≤n≤200000，答案可能超过 32 位。",
        ),
        _triplet(
            "R05", 2, "简单", ("栈", "括号匹配", "字符串"),
            ("括号串复核", "配置表达式检查", "代码片段括号校验"),
            (
                "判断只含 ()[]{} 的字符串是否正确嵌套，输出 YES 或 NO。",
                "检查配置表达式中的三类括号是否成对且嵌套正确。",
                "检查一段仅保留括号的代码结构是否合法。",
            ),
            (("{[()]}", "YES"), ("([]{})", "YES"), ("([{}])", "YES")),
            (("{[(])}", "NO"), ("((", "NO"), ("]", "NO")),
            ("右括号要匹配最近尚未配对的左括号。", "栈顶是唯一可能的匹配对象。", "左括号入栈；右括号检查并弹栈；最后栈为空。"),
            """s=input().strip(); st=[]; mp={')':'(',']':'[','}':'{'}\nfor c in s:\n if c in '([{': st.append(c)\n elif not st or st.pop()!=mp[c]: print('NO'); break\nelse: print('YES' if not st else 'NO')""",
            "O(n) 时间，O(n) 空间", ("弹栈前先判断空栈。", "扫描结束后仍有左括号也不合法。"),
            "输入一行括号字符串。", "合法输出 YES，否则输出 NO。", "字符串长度≤200000。",
        ),
        _triplet(
            "R06", 2, "中等", ("单调栈", "数组", "下一个更大"),
            ("等待更高温度", "等待更高价格", "下一次更高水位"),
            (
                "对每天温度，输出还需等待几天才出现严格更高温度；不存在输出 0。",
                "对每个时刻价格，输出距离下一次严格更高价格的步数；不存在输出 0。",
                "对每个水位记录，输出距离右侧首次更高水位的记录数；不存在输出 0。",
            ),
            (("5\n30 40 35 50 45", "1 2 1 0 0"), ("4\n5 4 6 7", "2 1 1 0"), ("6\n2 2 3 1 4 0", "2 1 2 1 0 0")),
            (("3\n3 2 1", "0 0 0"), ("1\n8", "0"), ("4\n1 1 1 2", "3 2 1 0")),
            ("需要寻找右侧第一个严格更大值的位置。", "单调栈保存尚未找到答案的下标。", "新值更大时持续弹栈，答案为当前下标减弹出下标。"),
            """import sys\nd=list(map(int,sys.stdin.buffer.read().split())); a=d[1:1+d[0]]; ans=[0]*len(a); st=[]\nfor i,x in enumerate(a):\n while st and a[st[-1]]<x:\n  j=st.pop(); ans[j]=i-j\n st.append(i)\nprint(*ans)""",
            "O(n) 时间，O(n) 空间", ("相等不算更高。", "栈里必须保存下标而非数值。"),
            "第一行 n，第二行 n 个整数。", "输出 n 个等待距离。", "1≤n≤200000。",
        ),
        _triplet(
            "R07", 3, "简单", ("双指针", "有序数组", "两数之和"),
            ("有序配对", "两件货物凑重量", "双人分数组合"),
            (
                "升序数组中寻找和为 target 的两个数，输出 1-based 下标；无解输出 -1 -1。",
                "按重量升序的货物中找两件总重为 target，输出其 1-based 位置。",
                "升序分数中找两人成绩和为目标值，输出其 1-based 位置。",
            ),
            (("5 9\n1 2 4 7 10", "2 4"), ("4 8\n1 3 5 7", "1 4"), ("6 0\n-5 -2 0 1 2 8", "2 5")),
            (("3 100\n1 2 3", "-1 -1"), ("2 6\n3 3", "1 2"), ("1 2\n2", "-1 -1")),
            ("数组有序，左右端点和决定移动方向。", "和偏小移动左指针，偏大移动右指针。", "while l<r；命中输出 l+1、r+1，否则输出 -1 -1。"),
            """import sys\nd=list(map(int,sys.stdin.buffer.read().split())); n,t=d[:2]; a=d[2:2+n]; l=0; r=n-1\nwhile l<r:\n s=a[l]+a[r]\n if s==t: print(l+1,r+1); break\n if s<t: l+=1\n else: r-=1\nelse: print(-1,-1)""",
            "O(n) 时间，O(n) 输入空间", ("同一个元素不能使用两次。", "无解时要有明确输出。"),
            "第一行 n、target，第二行升序数组。", "输出一组 1-based 下标或 -1 -1。", "1≤n≤200000。",
        ),
        _triplet(
            "R08", 3, "中等", ("二分查找", "计数", "有序数组"),
            ("批量出现次数", "库存编号计数", "成绩档位查询"),
            (
                "给定升序数组和 q 个查询，逐行输出每个查询值的出现次数。",
                "仓库编号已排序，对 q 个编号查询其库存条目数。",
                "分数已排序，对 q 个分数查询恰好等于该分数的人数。",
            ),
            (("7 3\n1 2 2 2 4 5 5\n2\n5\n3", "3\n2\n0"), ("5 2\n10 10 20 30 30\n10\n30", "2\n2"), ("6 3\n0 60 60 80 90 100\n60\n0\n70", "2\n1\n0")),
            (("1 2\n5\n5\n6", "1\n0"), ("4 1\n-2 -2 -2 -2\n-2", "4"), ("3 1\n1 2 3\n4", "0")),
            ("有序数组中次数等于右边界减左边界。", "bisect_left 找第一个等于位置，bisect_right 找最后一个之后。", "对每个 x 输出 bisect_right(a,x)-bisect_left(a,x)。"),
            """import sys\nfrom bisect import bisect_left,bisect_right\nd=list(map(int,sys.stdin.buffer.read().split())); n,q=d[:2]; a=d[2:2+n]\nfor x in d[2+n:2+n+q]: print(bisect_right(a,x)-bisect_left(a,x))""",
            "O((n+q) log n) 时间，O(n) 空间", ("查询值不存在时差值自然为 0。", "不要每次线性 count。"),
            "第一行 n、q，第二行升序数组，随后 q 个查询值。", "每个查询输出一行出现次数。", "1≤n,q≤200000。",
        ),
        _triplet(
            "R09", 3, "简单", ("前缀和", "区间查询", "数组"),
            ("连续区间总分", "每日流量查询", "账目区间净额"),
            (
                "回答 q 个 1-based 闭区间的元素和。",
                "给出每日流量，回答若干日期闭区间总流量。",
                "给出每日收支整数，回答若干闭区间净额。",
            ),
            (("5 3\n1 2 3 4 5\n1 1\n2 4\n1 5", "1\n9\n15"), ("4 2\n10 20 30 40\n1 3\n4 4", "60\n40"), ("5 2\n-3 5 -2 7 -1\n1 3\n2 5", "0\n9")),
            (("1 1\n-8\n1 1", "-8"), ("3 1\n0 0 0\n1 3", "0"), ("2 2\n5 -5\n1 2\n2 2", "0\n-5")),
            ("静态数组多次区间求和使用前缀和。", "pre[i] 表示前 i 个元素之和，并令 pre[0]=0。", "区间 [l,r] 为 pre[r]-pre[l-1]。"),
            """import sys\nd=list(map(int,sys.stdin.buffer.read().split())); n,q=d[:2]; a=d[2:2+n]; pre=[0]\nfor x in a: pre.append(pre[-1]+x)\np=2+n\nfor _ in range(q):\n l,r=d[p:p+2]; p+=2; print(pre[r]-pre[l-1])""",
            "O(n+q) 时间，O(n) 空间", ("1-based 左端点要减一。", "负数不会破坏前缀和。"),
            "第一行 n、q，第二行数组，随后 q 行 l r。", "逐行输出每个区间和。", "1≤n,q≤200000。",
        ),
        _triplet(
            "R10", 3, "中等", ("差分", "区间修改", "数组"),
            ("批量区间加法", "道路亮度调整", "座位区段积分"),
            (
                "初始数组给定，执行 q 次 1-based 闭区间加 k，输出最终数组。",
                "给出道路各段初始亮度，多次对连续区段增加整数亮度，输出最终值。",
                "给出座位初始积分，多次对连续编号区段加分，输出最终积分。",
            ),
            (("5 2\n1 1 1 1 1\n1 3 2\n2 5 -1", "3 2 2 0 0"), ("4 2\n0 5 0 5\n1 4 1\n2 3 2", "1 8 3 6"), ("3 1\n10 20 30\n2 2 -5", "10 15 30")),
            (("1 2\n0\n1 1 5\n1 1 -2", "3"), ("3 0\n1 2 3", "1 2 3"), ("2 1\n-1 -1\n1 2 -3", "-4 -4")),
            ("多次连续区间加法适合差分。", "先由原数组建立差分，再在 l 和 r+1 修改。", "恢复时对 diff 求前缀和。"),
            """import sys\nd=list(map(int,sys.stdin.buffer.read().split())); n,q=d[:2]; a=d[2:2+n]; diff=[0]*(n+1); prev=0\nfor i,x in enumerate(a): diff[i]=x-prev; prev=x\np=2+n\nfor _ in range(q):\n l,r,k=d[p:p+3]; p+=3; diff[l-1]+=k\n if r<n: diff[r]-=k\ncur=0; ans=[]\nfor i in range(n): cur+=diff[i]; ans.append(cur)\nprint(*ans)""",
            "O(n+q) 时间，O(n) 空间", ("r=n 时不存在 r+1 的有效元素。", "先建立原数组差分。"),
            "第一行 n、q，第二行初始数组，随后 q 行 l r k。", "一行输出最终数组。", "1≤n,q≤200000；q 可为 0。",
        ),
        _triplet(
            "R11", 3, "中等", ("DFS", "BFS", "连通块", "网格"),
            ("岛屿复查", "墨迹区域计数", "故障模块分组"),
            (
                "01 网格中四方向相邻的 1 属于同一岛屿，输出岛屿数量。",
                "字符网格中四方向相邻的 # 构成一块墨迹，输出墨迹块数量。",
                "01 模块图中 1 为故障，四方向相邻故障属于同组，输出组数。",
            ),
            (("3 4\n1100\n0010\n0011", "2"), ("3 3\n#..\n.##\n.#.", "2"), ("2 5\n10101\n11100", "2")),
            (("2 2\n00\n00", "0"), ("1 4\n####", "1"), ("3 1\n1\n0\n1", "2")),
            ("每发现一个未访问目标格，就得到一个新连通块。", "从该格开始 DFS/BFS，并标记所有四邻目标格。", "外层扫描计数，内层搜索；字符可能是 1 或 #。"),
            """from collections import deque\nn,m=map(int,input().split()); g=[list(input().strip()) for _ in range(n)]; target='#' if any('#' in row for row in g) else '1'; ans=0\nfor i in range(n):\n for j in range(m):\n  if g[i][j]!=target: continue\n  ans+=1; g[i][j]='.'; q=deque([(i,j)])\n  while q:\n   x,y=q.popleft()\n   for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):\n    nx,ny=x+dx,y+dy\n    if 0<=nx<n and 0<=ny<m and g[nx][ny]==target: g[nx][ny]='.'; q.append((nx,ny))\nprint(ans)""",
            "O(nm) 时间，O(nm) 最坏空间", ("只按四方向连接，不含对角。", "入队时立即标记。"),
            "第一行 n、m，随后 n 行等长网格。", "输出连通块数量。", "1≤n,m≤1000。",
        ),
        _triplet(
            "R12", 3, "中等", ("BFS", "最短路", "网格"),
            ("仓库最短路线", "机器人到达出口", "校园步行最短路"),
            (
                "网格中 S 到 T 可四方向走，# 不可走，输出最少步数，不可达为 -1。",
                "机器人从 S 到 E，四方向移动且不能经过 #，输出最少移动次数。",
                "校园地图从 A 到 B，四方向通过非 # 格，输出最短步数。",
            ),
            (("3 4\nS...\n.##.\n...T", "5"), ("3 3\nS#.\n...\n.#E", "4"), ("2 4\nA..#\n...B", "4")),
            (("2 2\nS#\n#T", "-1"), ("1 2\nSE", "1"), ("1 3\nA#B", "-1")),
            ("无权图最少步数使用 BFS。", "起点入队并标记距离 0，首次到达终点即最短。", "识别 S/A 为起点，T/E/B 为终点，四方向扩展。"),
            """from collections import deque\nn,m=map(int,input().split()); g=[input().strip() for _ in range(n)]; starts='SA'; ends='TEB'\nfor i in range(n):\n for j,c in enumerate(g[i]):\n  if c in starts: s=(i,j)\nq=deque([(s[0],s[1],0)]); seen={s}; ans=-1\nwhile q:\n x,y,d=q.popleft()\n if g[x][y] in ends: ans=d; break\n for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):\n  nx,ny=x+dx,y+dy\n  if 0<=nx<n and 0<=ny<m and g[nx][ny]!='#' and (nx,ny) not in seen: seen.add((nx,ny)); q.append((nx,ny,d+1))\nprint(ans)""",
            "O(nm) 时间与空间", ("访问标记要在入队时设置。", "不可达时保持 -1。"),
            "第一行 n、m，随后 n 行网格。", "输出最少步数或 -1。", "1≤n,m≤1000，恰有一个起点和终点。",
        ),
        _triplet(
            "R13", 2, "中等", ("树", "父节点数组", "遍历"),
            ("组织树高度", "目录层级统计", "课程依赖树概览"),
            (
                "给出每个节点父节点（根为 -1），输出树高（根高为 1）和叶子数。",
                "给出目录节点父编号，根为 -1，输出最大层数和无子目录节点数。",
                "给出课程树父编号，根为 -1，输出层数和叶子课程数。",
            ),
            (("5\n-1 0 0 1 1", "3 3"), ("4\n-1 0 1 2", "4 1"), ("6\n-1 0 0 2 2 4", "4 3")),
            (("1\n-1", "1 1"), ("3\n-1 0 0", "2 2"), ("4\n1 2 -1 2", "3 2")),
            ("父节点数组可建立孩子表。", "从根 BFS/DFS 计算深度；没有孩子的节点是叶子。", "找到 parent=-1 的根，队列保存 (节点,深度)。"),
            """from collections import deque\nimport sys\nd=list(map(int,sys.stdin.buffer.read().split())); n=d[0]; par=d[1:1+n]; children=[[] for _ in range(n)]\nfor i,p in enumerate(par):\n if p==-1: root=i\n else: children[p].append(i)\nq=deque([(root,1)]); height=0\nwhile q:\n u,h=q.popleft(); height=max(height,h)\n for v in children[u]: q.append((v,h+1))\nprint(height,sum(not c for c in children))""",
            "O(n) 时间与空间", ("根节点编号不一定是 0。", "单节点树既是根也是叶子。"),
            "第一行 n，第二行第 i 个整数为节点 i 的父节点。", "输出树高和叶子数。", "1≤n≤200000，输入保证构成一棵树。",
        ),
        _triplet(
            "R14", 2, "中等", ("并查集", "连通性", "在线查询"),
            ("社交连通查询", "网络线路合并", "城市道路连通"),
            (
                "处理 UNION a b 与 ASK a b；ASK 输出 YES/NO 表示是否连通。",
                "连接两台设备或查询两台设备是否处于同一网络。",
                "修建道路连接城市，并回答城市对是否连通。",
            ),
            (("5 5\nUNION 1 2\nASK 1 2\nASK 1 3\nUNION 2 3\nASK 1 3", "YES\nNO\nYES"), ("4 4\nUNION 1 4\nASK 4 1\nUNION 2 3\nASK 1 2", "YES\nNO"), ("3 3\nASK 1 1\nUNION 1 2\nASK 2 3", "YES\nNO")),
            (("2 2\nASK 1 2\nUNION 1 2", "NO"), ("1 1\nASK 1 1", "YES"), ("3 4\nUNION 1 2\nUNION 1 2\nASK 1 2\nASK 2 3", "YES\nNO")),
            ("需要支持动态合并与快速连通查询。", "并查集用 find 找根，union 合并不同根。", "ASK 比较 find(a)==find(b)，路径压缩降低代价。"),
            """import sys\nlines=sys.stdin.buffer.readlines(); n,q=map(int,lines[0].split()); p=list(range(n+1)); sz=[1]*(n+1)\ndef find(x):\n while x!=p[x]: p[x]=p[p[x]]; x=p[x]\n return x\nfor line in lines[1:1+q]:\n op,a,b=line.split(); a=int(a); b=int(b); ra=find(a); rb=find(b)\n if op==b'ASK': print('YES' if ra==rb else 'NO')\n elif ra!=rb:\n  if sz[ra]<sz[rb]: ra,rb=rb,ra\n  p[rb]=ra; sz[ra]+=sz[rb]""",
            "近似 O(qα(n)) 时间，O(n) 空间", ("重复 UNION 不应破坏大小。", "ASK 自己与自己总是连通。"),
            "第一行 n、q，随后 q 行命令和两个 1-based 节点。", "每个 ASK 输出一行 YES 或 NO。", "1≤n,q≤200000。",
        ),
        _triplet(
            "R15", 6, "中等", ("拓扑排序", "有向图", "堆"),
            ("任务执行顺序", "课程安排顺序", "构建依赖排序"),
            (
                "给出 u→v 依赖，输出字典序最小拓扑序；有环输出 IMPOSSIBLE。",
                "u 是 v 的先修课，输出编号最小优先的可行修课序；有环输出 IMPOSSIBLE。",
                "构建步骤 u 必须早于 v，输出字典序最小顺序；有环输出 IMPOSSIBLE。",
            ),
            (("4 3\n1 3\n2 3\n3 4", "1 2 3 4"), ("5 4\n1 4\n2 4\n3 5\n4 5", "1 2 3 4 5"), ("3 2\n2 3\n1 3", "1 2 3")),
            (("2 2\n1 2\n2 1", "IMPOSSIBLE"), ("3 0", "1 2 3"), ("3 3\n1 2\n2 3\n3 1", "IMPOSSIBLE")),
            ("拓扑排序反复选择入度为 0 的点。", "要字典序最小，零入度集合用小根堆。", "弹出 u，减少邻点入度；输出不足 n 个说明有环。"),
            """import heapq,sys\nd=list(map(int,sys.stdin.buffer.read().split())); n,m=d[:2]; g=[[] for _ in range(n+1)]; deg=[0]*(n+1); p=2\nfor _ in range(m): u,v=d[p:p+2]; p+=2; g[u].append(v); deg[v]+=1\nh=[i for i in range(1,n+1) if deg[i]==0]; heapq.heapify(h); ans=[]\nwhile h:\n u=heapq.heappop(h); ans.append(u)\n for v in g[u]:\n  deg[v]-=1\n  if deg[v]==0: heapq.heappush(h,v)\nprint(*ans) if len(ans)==n else print('IMPOSSIBLE')""",
            "O((n+m) log n) 时间，O(n+m) 空间", ("普通队列不能保证字典序最小。", "无边图要输出全部节点。"),
            "第一行 n、m，随后 m 行有向边 u v。", "输出拓扑序或 IMPOSSIBLE。", "1≤n≤200000。",
        ),
        _triplet(
            "R16", 6, "中等", ("Dijkstra", "最短路", "堆"),
            ("城市最短路", "网络最小延迟", "物流最低里程"),
            (
                "非负无向带权图中求 s 到 t 的最短距离，不可达输出 -1。",
                "设备网络边延迟非负，求 s 到 t 最小总延迟，不可达输出 -1。",
                "道路里程非负，求仓库 s 到客户 t 的最短里程，不可达输出 -1。",
            ),
            (("4 4 1 4\n1 2 2\n2 4 5\n1 3 10\n3 4 1", "7"), ("3 3 1 3\n1 2 4\n2 3 2\n1 3 9", "6"), ("5 4 2 5\n2 1 1\n1 3 2\n3 4 3\n4 5 4", "10")),
            (("3 1 1 3\n1 2 5", "-1"), ("1 0 1 1", "0"), ("2 2 1 2\n1 2 9\n1 2 3", "3")),
            ("非负边权最短路使用 Dijkstra。", "小根堆保存候选距离，弹出过期距离时跳过。", "松弛 nd=dist[u]+w；若更小就更新并入堆。"),
            """import heapq,sys\nd=list(map(int,sys.stdin.buffer.read().split())); n,m,s,t=d[:4]; g=[[] for _ in range(n+1)]; p=4\nfor _ in range(m): u,v,w=d[p:p+3]; p+=3; g[u].append((v,w)); g[v].append((u,w))\nINF=10**30; dist=[INF]*(n+1); dist[s]=0; h=[(0,s)]\nwhile h:\n du,u=heapq.heappop(h)\n if du!=dist[u]: continue\n for v,w in g[u]:\n  nd=du+w\n  if nd<dist[v]: dist[v]=nd; heapq.heappush(h,(nd,v))\nprint(dist[t] if dist[t]<INF else -1)""",
            "O((n+m) log n) 时间，O(n+m) 空间", ("无向边要加两个方向。", "负权图不能使用 Dijkstra。"),
            "第一行 n、m、s、t，随后 m 行无向边 u v w。", "输出最短距离或 -1。", "1≤n≤200000，0≤w≤10^9。",
        ),
        _triplet(
            "R17", 4, "中等", ("回溯", "子集", "剪枝"),
            ("目标和子集数量", "选课学分组合", "货物装载组合"),
            (
                "给出互不相同的正整数，统计选取若干数使和为 target 的子集数。",
                "每门课至多选一次，统计总学分恰为 target 的选课方案数。",
                "每件货物至多选一次，统计总重量恰为 target 的装载方案数。",
            ),
            (("4 5\n1 2 3 4", "2"), ("5 6\n1 2 3 4 5", "3"), ("4 7\n2 3 4 5", "2")),
            (("3 1\n2 3 4", "0"), ("1 5\n5", "1"), ("3 0\n1 2 3", "1")),
            ("每个元素只有选择或跳过两种决策。", "正数排序后，当前和超过目标可停止该分支。", "dfs(i,remain)：不选进入 i+1；可选时选择并进入 i+1。"),
            """import sys\nd=list(map(int,sys.stdin.buffer.read().split())); n,t=d[:2]; a=sorted(d[2:2+n]); ans=0\ndef dfs(i,remain):\n global ans\n if remain==0: ans+=1; return\n if i==n or a[i]>remain: return\n dfs(i+1,remain); dfs(i+1,remain-a[i])\ndfs(0,t); print(ans)""",
            "O(2^n) 最坏时间，O(n) 递归栈", ("target=0 时空集是一种方案。", "每个元素最多选一次，递归进入 i+1。"),
            "第一行 n、target，第二行 n 个互异正整数。", "输出符合条件的子集数量。", "1≤n≤25，0≤target。",
        ),
        _triplet(
            "R18", 4, "中等", ("贪心", "区间", "排序"),
            ("最多活动安排", "最多会议预订", "最多作业时段"),
            (
                "从若干半开区间 [l,r) 中选择最多个互不重叠区间，端点相等可衔接。",
                "会议室只能同时容纳一场会议，求最多可安排会议数。",
                "单台机器选择最多个不重叠作业时段，求数量。",
            ),
            (("5\n1 3\n2 5\n3 4\n4 7\n6 8", "3"), ("4\n0 2\n1 4\n2 3\n3 5", "3"), ("3\n1 10\n2 3\n4 5", "2")),
            (("1\n5 9", "1"), ("3\n1 2\n2 3\n3 4", "3"), ("3\n0 5\n0 5\n0 5", "1")),
            ("选择结束最早的区间，为后续保留最多空间。", "按右端点升序排序，记录上次选中区间终点。", "若 l>=end 则选择并更新 end=r。"),
            """n=int(input()); a=sorted((tuple(map(int,input().split())) for _ in range(n)),key=lambda x:x[1]); ans=0; end=None\nfor l,r in a:\n if end is None or l>=end: ans+=1; end=r\nprint(ans)""",
            "O(n log n) 时间，O(n) 空间", ("按开始时间贪心通常不正确。", "端点相等允许衔接。"),
            "第一行 n，随后 n 行区间 l r。", "输出最多可选择区间数。", "1≤n≤200000，l<r。",
        ),
        _triplet(
            "R19", 4, "简单", ("动态规划", "滚动变量", "不相邻选择"),
            ("不相邻房屋收益", "隔日训练最高积分", "相邻冲突任务收益"),
            (
                "不能选择相邻位置，求数组中可选元素最大和；允许全不选。",
                "连续两天不能都训练，给出每天积分，求最大总积分。",
                "相邻任务冲突不能同时做，给出收益，求最大收益。",
            ),
            (("5\n2 7 9 3 1", "12"), ("4\n5 1 1 5", "10"), ("6\n4 2 3 9 1 6", "19")),
            (("1\n-5", "0"), ("3\n0 0 0", "0"), ("2\n8 9", "9")),
            ("到位置 i 的最优只有选 i 或不选 i。", "不选继承前一状态；选则来自前两状态加当前值。", "new=max(prev1, prev2+x)，然后滚动。"),
            """import sys\nd=list(map(int,sys.stdin.buffer.read().split())); a=d[1:1+d[0]]; prev2=prev1=0\nfor x in a: prev2,prev1=prev1,max(prev1,prev2+x)\nprint(prev1)""",
            "O(n) 时间，O(1) 空间", ("允许全不选，所以全负时答案为 0。", "更新两个变量时要使用旧值。"),
            "第一行 n，第二行 n 个整数收益。", "输出不选择相邻元素的最大和。", "1≤n≤200000。",
        ),
        _triplet(
            "R20", 4, "中等", ("动态规划", "0/1背包", "滚动数组"),
            ("背包价值复习", "服务器容量分配", "实验器材装箱"),
            (
                "n 件物品各有重量和价值，每件最多一次，在容量 W 内求最大价值。",
                "n 个任务占用容量并产生收益，每个最多部署一次，求容量 W 内最大收益。",
                "n 件器材各有重量和评分，每件最多装一次，求不超载时最高总评分。",
            ),
            (("4 5\n2 3\n1 2\n3 4\n2 2", "7"), ("3 4\n3 8\n2 5\n1 2", "10"), ("5 6\n2 4\n3 5\n4 7\n1 1\n2 3", "11")),
            (("2 1\n2 100\n3 200", "0"), ("1 3\n3 9", "9"), ("3 4\n2 5\n2 5\n4 9", "10")),
            ("每件物品只有选或不选。", "一维 dp[j] 表示容量 j 的最大价值。", "每件物品的容量 j 必须从 W 倒序到 weight。"),
            """import sys\nd=list(map(int,sys.stdin.buffer.read().split())); n,W=d[:2]; dp=[0]*(W+1); p=2\nfor _ in range(n):\n w,v=d[p:p+2]; p+=2\n for j in range(W,w-1,-1): dp[j]=max(dp[j],dp[j-w]+v)\nprint(dp[W])""",
            "O(nW) 时间，O(W) 空间", ("容量正序会把同一物品使用多次。", "装不下任何物品时答案为 0。"),
            "第一行 n、W，随后 n 行重量和价值。", "输出容量限制内最大价值。", "1≤n≤1000，1≤W≤10000。",
        ),
    ),
    (),
)
