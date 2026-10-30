import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
NB_PATH = ROOT / "math_modeling_experiments" / "notebooks" / "04_campus_running_path_planning_model.ipynb"


cells = []


def md(text, cell_id):
    cells.append(
        {
            "cell_type": "markdown",
            "id": cell_id,
            "metadata": {},
            "source": text.splitlines(keepends=True),
        }
    )


def code(text, cell_id):
    cells.append(
        {
            "cell_type": "code",
            "execution_count": None,
            "id": cell_id,
            "metadata": {},
            "outputs": [],
            "source": text.splitlines(keepends=True),
        }
    )


md(
    """# 校园跑步打卡路径规划与低聚集打卡点生成模型 v2

本 Notebook 在 v1 的地图识别、道路骨架化、路网构建、最短路计算和路线可视化基础上，重构两个核心问题：

1. **给定 5 个打卡点后的最优访问顺序规划**：作为精确的可行性检验器和路径规划器。
2. **随机生成 10 组新的打卡点**：要求每组存在至少一条可行路线，且规划顺序中相邻打卡点之间不超过 3 条道路，同时尽量减少多组学生同时跑步时的路线聚集。

v2 明确区分“给定点后的访问顺序优化”和“从校园候选点池中生成打卡点”两个子问题。穷举法仍然保留，但只作为 5 点路线规划模块；打卡点生成则通过 baseline 和多目标低聚集算法进行对比。""",
    "title",
)

md(
    """## 1. 问题重述

跑步打卡系统为学生随机生成 5 个打卡点，学生可以按照任意顺序跑到这些点，并通过卫星定位完成打卡。由于相邻两次打卡之间存在时间限制，打卡点的空间分布和访问顺序都会影响完成效率。

本实验需要解决两个子问题：

**子问题 A：给定 5 个打卡点后的路径规划**

- 输入：一组 5 个打卡点；
- 输出：访问顺序、最短路线、总路程、最大相邻道路段数、最大相邻时间；
- 方法：先计算两两最短路，再枚举 `5! = 120` 种访问顺序；
- 作用：作为可行性检验器和给定 5 点下的最优访问顺序求解器。

**子问题 B：随机生成 10 组新的打卡点**

- 输入：校园道路段拓扑图和候选打卡点池；
- 输出：10 组打卡点，每组 5 个点；
- 约束：每组必须存在至少一条访问顺序，使相邻打卡点之间不超过 3 条道路；
- 优化目标：减少不同组路线之间的共享道路段，降低同时跑步时的聚集风险。

穷举法不能直接解决打卡点生成问题，因为它只能枚举给定 5 点的访问顺序，不能从整个校园候选点池中穷举选 5 点。若候选点池有 `N` 个点，直接枚举组合需要检查 `C(N,5)` 组，组合数量会迅速变得不可接受。因此，本实验将穷举法作为内部精确检验器，而不是最终生成算法。""",
    "problem-restatement",
)

md(
    """## 2. 数据读取与地图预处理

本节读取校园地图和附件中的打卡点坐标。附件 2 当前实际包含 5 名同学，每名同学有 1 个文字起点和 5 个打卡点坐标。由于文字起点没有像素坐标，本文重点优化 5 个打卡点之间的访问顺序；若后续补充起点坐标，可将起点作为固定首点加入路线规划函数。""",
    "data-intro",
)

code(
    """from collections import defaultdict
from functools import lru_cache
from itertools import permutations
from pathlib import Path
from time import perf_counter

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import networkx as nx
from PIL import Image
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from skimage.color import rgb2hsv
from skimage.measure import label, regionprops
from skimage.morphology import (
    binary_closing,
    binary_dilation,
    binary_opening,
    disk,
    remove_small_objects,
    skeletonize,
)

random_seed = 42
rng_global = np.random.default_rng(random_seed)

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

for candidate in [Path.cwd(), *Path.cwd().parents]:
    if (candidate / 'E3 - 校园跑步路径的规划').exists():
        PROJECT_ROOT = candidate
        break
else:
    raise FileNotFoundError('没有找到 E3 - 校园跑步路径的规划 文件夹，请检查当前工作目录。')

DATA_DIR = PROJECT_ROOT / 'E3 - 校园跑步路径的规划' / '附件：上海理理工大学跑步打卡'
MAP_PATH = DATA_DIR / '附件1：上海理工大学校园道路图.jpg'
POINTS_PATH = DATA_DIR / '附件2：打卡位置数据.xlsx'
OUTPUT_DIR = PROJECT_ROOT / 'math_modeling_experiments' / 'outputs'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ASSUMED_M_PER_PIXEL = 0.45
RUNNING_SPEED_M_PER_MIN = 160.0
MAX_SEGMENT_COUNT = 3
N_GROUPS = 10
POINTS_PER_GROUP = 5

MAP_PATH, POINTS_PATH, OUTPUT_DIR""",
    "imports-and-paths",
)

code(
    """raw_points = pd.read_excel(POINTS_PATH)
raw_points = raw_points.rename(columns={raw_points.columns[0]: '学生'})
y_columns = ['y1', 'y2', 'y3', 'y4', 'y5']
if 'y5' not in raw_points.columns and 'y6' in raw_points.columns:
    y_columns[-1] = 'y6'

point_records = []
for _, row in raw_points.iterrows():
    for i in range(1, 6):
        point_records.append({
            '学生': row['学生'],
            '文字起点': row['起点'],
            '打卡点': f'P{i}',
            'x': float(row[f'x{i}']),
            'y': float(row[y_columns[i - 1]]),
        })
points_long = pd.DataFrame(point_records)

display(raw_points)
display(points_long.head(10))""",
    "read-checkpoint-data",
)

md(
    """## 3. 校园道路图识别与路网建模

本节保留 v1 的地图识别主流程：缩小原图、使用 HSV 颜色空间定位校园主体和道路区域、骨架化道路区域，并把道路骨架转化为加权无向图。节点为道路骨架像素点，边连接相邻骨架像素，边权为原图像素尺度下的欧氏距离。""",
    "road-model-intro",
)

code(
    """def build_pixel_graph(skeleton, scale):
    ys, xs = np.nonzero(skeleton)
    node_id = -np.ones(skeleton.shape, dtype=int)
    node_id[ys, xs] = np.arange(len(xs))

    graph = nx.Graph()
    for idx, (y, x) in enumerate(zip(ys, xs)):
        graph.add_node(idx, pos=(x / scale, y / scale), grid=(int(y), int(x)))

    for idx, (y, x) in enumerate(zip(ys, xs)):
        for dy, dx in [(0, 1), (1, 0), (1, 1), (1, -1)]:
            yy, xx = y + dy, x + dx
            if 0 <= yy < skeleton.shape[0] and 0 <= xx < skeleton.shape[1]:
                neighbor = node_id[yy, xx]
                if neighbor >= 0:
                    graph.add_edge(idx, int(neighbor), weight=float(np.hypot(dx, dy) / scale))
    return graph


def extract_road_network(image_path, scale=0.20):
    image = Image.open(image_path).convert('RGB')
    small_size = (int(image.width * scale), int(image.height * scale))
    small_image = image.resize(small_size, Image.Resampling.LANCZOS)
    rgb = np.asarray(small_image) / 255.0

    hsv = rgb2hsv(rgb)
    saturation = hsv[..., 1]
    value = hsv[..., 2]

    colored_mask = (saturation > 0.25) & (value > 0.25)
    colored_mask = remove_small_objects(colored_mask, min_size=80)

    campus_mask = binary_dilation(colored_mask, disk(16))
    campus_mask = binary_closing(campus_mask, disk(18))
    campus_mask = ndi.binary_fill_holes(campus_mask)
    labeled = label(campus_mask)
    regions = sorted(regionprops(labeled), key=lambda r: r.area, reverse=True)
    if not regions:
        raise RuntimeError('未能识别校园主体区域，请调整颜色阈值。')
    campus_mask = labeled == regions[0].label

    road_mask = (saturation < 0.18) & (value > 0.78) & campus_mask
    road_mask = remove_small_objects(road_mask, min_size=150)
    road_mask = binary_opening(road_mask, disk(1))
    road_mask = binary_closing(road_mask, disk(2))

    skeleton = skeletonize(road_mask)
    labeled_skeleton = label(skeleton)
    skeleton_regions = sorted(regionprops(labeled_skeleton), key=lambda r: r.area, reverse=True)
    if not skeleton_regions:
        raise RuntimeError('未能提取道路骨架，请调整道路阈值。')
    skeleton = labeled_skeleton == skeleton_regions[0].label

    graph = build_pixel_graph(skeleton, scale)
    return {
        'image': image,
        'rgb_small': rgb,
        'scale': scale,
        'campus_mask': campus_mask,
        'road_mask': road_mask,
        'skeleton': skeleton,
        'graph': graph,
    }

network_data = extract_road_network(MAP_PATH, scale=0.20)
G = network_data['graph']

road_summary = pd.DataFrame({
    '指标': ['缩放比例', '道路掩膜像素数', '道路骨架节点数', '道路骨架边数', '连通分量数'],
    '数值': [
        network_data['scale'],
        int(network_data['road_mask'].sum()),
        G.number_of_nodes(),
        G.number_of_edges(),
        nx.number_connected_components(G),
    ],
})
road_summary""",
    "extract-road-network",
)

code(
    """fig, axes = plt.subplots(1, 3, figsize=(16, 5))
axes[0].imshow(network_data['rgb_small'])
axes[0].set_title('原始校园地图缩略图')
axes[1].imshow(network_data['road_mask'], cmap='gray')
axes[1].set_title('识别出的道路区域')

graph_scale = network_data['scale']
edge_segments = []
edge_weights = []
for u, v, data in G.edges(data=True):
    x1, y1 = G.nodes[u]['pos']
    x2, y2 = G.nodes[v]['pos']
    edge_segments.append([(x1 * graph_scale, y1 * graph_scale), (x2 * graph_scale, y2 * graph_scale)])
    edge_weights.append(data['weight'])
edge_weights = np.array(edge_weights)
line_collection = LineCollection(edge_segments, cmap='viridis', linewidths=0.45, alpha=0.9)
line_collection.set_array(edge_weights)
line_collection.set_clim(edge_weights.min(), edge_weights.max())
axes[2].add_collection(line_collection)
node_positions = np.array([G.nodes[node]['pos'] for node in G.nodes()]) * graph_scale
axes[2].scatter(node_positions[::25, 0], node_positions[::25, 1], s=1, color='black', alpha=0.35)
axes[2].set_xlim(0, network_data['rgb_small'].shape[1])
axes[2].set_ylim(network_data['rgb_small'].shape[0], 0)
axes[2].set_aspect('equal')
axes[2].set_title('加权无向路网图表示')
axes[2].text(
    0.02, 0.04,
    f\"节点数：{G.number_of_nodes()}\\n边数：{G.number_of_edges()}\\n边权：原图像素欧氏距离\",
    transform=axes[2].transAxes,
    fontsize=9,
    bbox=dict(facecolor='white', alpha=0.85, edgecolor='none'),
)
colorbar = fig.colorbar(line_collection, ax=axes[2], fraction=0.046, pad=0.03)
colorbar.set_label('边权（原图像素距离）')
for ax in axes:
    ax.axis('off')
plt.tight_layout()
road_extraction_path = OUTPUT_DIR / 'e3_road_extraction.png'
plt.savefig(road_extraction_path, dpi=200, bbox_inches='tight')
plt.show()
print('道路识别与加权无向图已保存：', road_extraction_path)""",
    "plot-road-extraction",
)

md(
    """## 4. 道路段拓扑图构建

像素级路网足够精细，但不适合表达“经过几条道路”。因此 v2 在像素骨架图基础上构造道路段拓扑图：

- 度数不等于 2 的骨架节点视为路口或端点；
- 两个路口之间连续的一段骨架视为 1 条道路段；
- 道路段边权为该段骨架在原图像素尺度下的长度。

后续打卡点生成和 3 条道路约束都基于这个道路段拓扑图。""",
    "segment-graph-intro",
)

code(
    """def simplify_to_road_segment_graph(graph):
    degree = dict(graph.degree())
    critical_nodes = {node for node, deg in degree.items() if deg != 2}

    segment_graph = nx.Graph()
    for node in critical_nodes:
        segment_graph.add_node(node, pos=graph.nodes[node]['pos'])

    visited_edges = set()
    for start in critical_nodes:
        for neighbor in graph.neighbors(start):
            first_edge = tuple(sorted((start, neighbor)))
            if first_edge in visited_edges:
                continue
            visited_edges.add(first_edge)

            path = [start, neighbor]
            length = graph.edges[start, neighbor]['weight']
            previous, current = start, neighbor

            while current not in critical_nodes:
                next_nodes = [node for node in graph.neighbors(current) if node != previous]
                if not next_nodes:
                    break
                nxt = next_nodes[0]
                edge = tuple(sorted((current, nxt)))
                if edge in visited_edges:
                    break
                visited_edges.add(edge)
                length += graph.edges[current, nxt]['weight']
                path.append(nxt)
                previous, current = current, nxt

            end = current
            if start != end and end in critical_nodes:
                if segment_graph.has_edge(start, end):
                    if length < segment_graph.edges[start, end]['weight']:
                        segment_graph.edges[start, end].update(weight=length, geometry=tuple(path))
                else:
                    segment_graph.add_edge(start, end, weight=length, geometry=tuple(path))

    largest_component = max(nx.connected_components(segment_graph), key=len)
    return segment_graph.subgraph(largest_component).copy()

segment_graph = simplify_to_road_segment_graph(G)
H = segment_graph
segment_summary = pd.DataFrame({
    '指标': ['路口/端点数量', '道路段数量', '连通分量数', '平均道路段长度(像素)'],
    '数值': [
        H.number_of_nodes(),
        H.number_of_edges(),
        nx.number_connected_components(H),
        np.mean([data['weight'] for _, _, data in H.edges(data=True)]),
    ],
})
segment_summary.round(2)""",
    "build-segment-graph",
)

code(
    """# 道路段拓扑图可视化：节点为路口/端点，边为两路口之间的一整段道路。
segment_lines = []
segment_weights = []
for u, v, data in H.edges(data=True):
    geometry = np.array([G.nodes[node]['pos'] for node in data['geometry']]) * network_data['scale']
    if len(geometry) < 2:
        continue
    for p1, p2 in zip(geometry[:-1], geometry[1:]):
        segment_lines.append([p1, p2])
        segment_weights.append(data['weight'])

segment_weights = np.array(segment_weights)
fig, axes = plt.subplots(1, 2, figsize=(15, 7))

axes[0].imshow(network_data['rgb_small'])
line_collection = LineCollection(segment_lines, cmap='plasma', linewidths=1.0, alpha=0.85)
line_collection.set_array(segment_weights)
axes[0].add_collection(line_collection)
node_xy = np.array([H.nodes[node]['pos'] for node in H.nodes()]) * network_data['scale']
axes[0].scatter(node_xy[:, 0], node_xy[:, 1], s=6, color='black', alpha=0.55, label='路口/端点')
axes[0].set_title('道路段拓扑图叠加在校园地图上')
axes[0].axis('off')
axes[0].legend(loc='lower left')
cbar = fig.colorbar(line_collection, ax=axes[0], fraction=0.046, pad=0.03)
cbar.set_label('道路段长度（原图像素）')

axes[1].set_facecolor('#f8f8f8')
plain_collection = LineCollection(segment_lines, colors='#4c78a8', linewidths=0.75, alpha=0.85)
axes[1].add_collection(plain_collection)
axes[1].scatter(node_xy[:, 0], node_xy[:, 1], s=4, color='#222222', alpha=0.5)
axes[1].set_xlim(0, network_data['rgb_small'].shape[1])
axes[1].set_ylim(network_data['rgb_small'].shape[0], 0)
axes[1].set_aspect('equal')
axes[1].set_title('抽象道路段拓扑图')
axes[1].text(
    0.02,
    0.04,
    f\"路口/端点：{H.number_of_nodes()}\\n道路段：{H.number_of_edges()}\\n约束定义：相邻打卡点最短路径边数 <= 3\",
    transform=axes[1].transAxes,
    fontsize=10,
    bbox=dict(facecolor='white', alpha=0.9, edgecolor='none'),
)
axes[1].axis('off')

plt.tight_layout()
segment_topology_path = OUTPUT_DIR / 'e3_segment_topology_graph.png'
plt.savefig(segment_topology_path, dpi=220, bbox_inches='tight')
plt.show()
print('道路段拓扑图已保存：', segment_topology_path)""",
    "plot-segment-topology-graph",
)

md(
    """## 5. 给定打卡点的路径规划模型

本节实现统一函数 `plan_route_for_points(points, segment_graph, distance_cache=None)`。

它的作用不是生成打卡点，而是在给定 5 个打卡点后，精确判断这组点是否存在可行访问顺序，并求出总路程最短的可行顺序。由于每组只有 5 个点，访问顺序只有 120 种，穷举法在这里是可接受且精确的。""",
    "route-planner-intro",
)

code(
    """def normalize_edge(a, b):
    return tuple(sorted((int(a), int(b))))


def pair_shortest_path_info(u, v, segment_graph, distance_cache=None):
    if distance_cache is None:
        distance_cache = {}
    key = normalize_edge(u, v)
    if key not in distance_cache:
        path = nx.shortest_path(segment_graph, int(u), int(v), weight='weight')
        distance = nx.path_weight(segment_graph, path, weight='weight')
        edge_path = tuple(normalize_edge(a, b) for a, b in zip(path[:-1], path[1:]))
        distance_cache[key] = {
            'distance': float(distance),
            'road_count': len(edge_path),
            'node_path': tuple(path),
            'edge_path': edge_path,
        }
    return distance_cache[key]


def point_to_node(point):
    if isinstance(point, dict):
        return int(point['node'])
    if hasattr(point, '__getitem__'):
        return int(point['node'])
    return int(point)


def point_to_id(point, fallback_index):
    if isinstance(point, dict):
        return point.get('candidate_id', point.get('point_id', fallback_index))
    if hasattr(point, '__getitem__') and 'candidate_id' in point:
        return point['candidate_id']
    return fallback_index


def plan_route_for_points(points, segment_graph, distance_cache=None, max_segment_count=MAX_SEGMENT_COUNT):
    if distance_cache is None:
        distance_cache = {}
    if len(points) != POINTS_PER_GROUP:
        raise ValueError(f'每组打卡点必须为 {POINTS_PER_GROUP} 个。')

    nodes = [point_to_node(point) for point in points]
    point_ids = [point_to_id(point, i) for i, point in enumerate(points)]

    pair_info = {}
    for i, j in permutations(range(len(nodes)), 2):
        if i < j:
            pair_info[(i, j)] = pair_shortest_path_info(nodes[i], nodes[j], segment_graph, distance_cache)

    best = None
    evaluated_orders = []
    for order in permutations(range(len(nodes))):
        total_distance = 0.0
        max_pair_distance = 0.0
        max_segment_count_seen = 0
        full_edge_path = []
        feasible = True
        for left, right in zip(order[:-1], order[1:]):
            key = tuple(sorted((left, right)))
            info = pair_info[key]
            if info['road_count'] > max_segment_count:
                feasible = False
                break
            total_distance += info['distance']
            max_pair_distance = max(max_pair_distance, info['distance'])
            max_segment_count_seen = max(max_segment_count_seen, info['road_count'])
            full_edge_path.extend(info['edge_path'])
        if not feasible:
            continue
        result = {
            'feasible': True,
            'order': tuple(order),
            'ordered_point_ids': tuple(point_ids[i] for i in order),
            'ordered_nodes': tuple(nodes[i] for i in order),
            'total_distance': float(total_distance),
            'max_segment_count': int(max_segment_count_seen),
            'max_pair_distance': float(max_pair_distance),
            'edge_path': tuple(full_edge_path),
            'used_edges': frozenset(full_edge_path),
        }
        evaluated_orders.append(result)
        if best is None or result['total_distance'] < best['total_distance']:
            best = result

    if best is None:
        return {
            'feasible': False,
            'order': None,
            'ordered_point_ids': None,
            'ordered_nodes': None,
            'total_distance': np.inf,
            'max_segment_count': np.inf,
            'max_pair_distance': np.inf,
            'edge_path': tuple(),
            'used_edges': frozenset(),
        }
    best['evaluated_feasible_orders'] = len(evaluated_orders)
    return best


def route_pixel_geometry_from_edges(edge_path, segment_graph=H, pixel_graph=G):
    pixel_nodes = []
    for edge in edge_path:
        a, b = edge
        geometry = list(segment_graph.edges[a, b]['geometry'])
        if geometry[0] != a:
            geometry = geometry[::-1]
        if not pixel_nodes:
            pixel_nodes.extend(geometry)
        else:
            pixel_nodes.extend(geometry[1:])
    if not pixel_nodes:
        return np.empty((0, 2))
    return np.array([pixel_graph.nodes[node]['pos'] for node in pixel_nodes])

print('路径规划函数已定义。')""",
    "plan-route-function",
)

code(
    """segment_nodes = np.array(list(H.nodes()))
segment_positions = np.array([H.nodes[n]['pos'] for n in segment_nodes])
segment_tree = cKDTree(segment_positions)

def nearest_segment_node(x, y):
    distance, index = segment_tree.query([x, y])
    return int(segment_nodes[index]), float(distance)

attachment_records = []
attachment_route_details = {}
attachment_distance_cache = {}
for student, group in points_long.groupby('学生', sort=False):
    group = group.sort_values('打卡点').reset_index(drop=True)
    points = []
    projection_errors = []
    for _, row in group.iterrows():
        node, error = nearest_segment_node(row['x'], row['y'])
        points.append({'candidate_id': row['打卡点'], 'node': node, 'x': row['x'], 'y': row['y']})
        projection_errors.append(error)
    plan = plan_route_for_points(points, H, distance_cache=attachment_distance_cache)
    attachment_route_details[student] = {'points': points, 'plan': plan}
    attachment_records.append({
        '学生': student,
        '文字起点': group['文字起点'].iloc[0],
        'feasible': plan['feasible'],
        'order': ' -> '.join(plan['ordered_point_ids']) if plan['feasible'] else '不可行',
        'total_distance': plan['total_distance'],
        'max_segment_count': plan['max_segment_count'],
        'max_pair_distance': plan['max_pair_distance'],
        'max_pair_time_min': plan['max_pair_distance'] * ASSUMED_M_PER_PIXEL / RUNNING_SPEED_M_PER_MIN if plan['feasible'] else np.inf,
        'used_edge_count': len(plan['used_edges']),
        '平均投影误差': np.mean(projection_errors),
    })

attachment_route_df = pd.DataFrame(attachment_records)
attachment_route_df.round(3)""",
    "plan-attachment-routes",
)

md(
    """## 6. 打卡点生成问题建模

打卡点生成问题与给定 5 点后的路径规划不同。生成问题需要从整个候选点池中选择 10 组点，每组 5 个，并同时满足可行性和低聚集目标。

候选点池基于道路段拓扑图生成，优先使用路口节点和道路端点；同时从较长道路段中补充少量道路段中点。为避免候选点过密，使用空间距离阈值去重。""",
    "candidate-pool-intro",
)

code(
    """def build_candidate_pool(segment_graph, min_distance_px=55.0, max_candidates=520, random_seed=42):
    rng = np.random.default_rng(random_seed)
    candidate_records = []
    node_items = list(segment_graph.nodes())
    rng.shuffle(node_items)
    selected_positions = []

    for node in node_items:
        x, y = segment_graph.nodes[node]['pos']
        pos = np.array([x, y])
        if selected_positions:
            distances = np.linalg.norm(np.array(selected_positions) - pos, axis=1)
            if distances.min() < min_distance_px:
                continue
        candidate_records.append({
            'candidate_id': f'N{len(candidate_records):04d}',
            'node': int(node),
            'x': float(x),
            'y': float(y),
            'candidate_type': '路口/端点',
        })
        selected_positions.append(pos)
        if len(candidate_records) >= int(max_candidates * 0.88):
            break

    long_edges = sorted(segment_graph.edges(data=True), key=lambda item: item[2]['weight'], reverse=True)
    for u, v, data in long_edges:
        if len(candidate_records) >= max_candidates:
            break
        if data['weight'] < 120:
            continue
        x1, y1 = segment_graph.nodes[u]['pos']
        x2, y2 = segment_graph.nodes[v]['pos']
        midpoint = np.array([(x1 + x2) / 2, (y1 + y2) / 2])
        if selected_positions:
            distances = np.linalg.norm(np.array(selected_positions) - midpoint, axis=1)
            if distances.min() < min_distance_px:
                continue
        anchor = int(u)
        candidate_records.append({
            'candidate_id': f'M{len(candidate_records):04d}',
            'node': anchor,
            'x': float(midpoint[0]),
            'y': float(midpoint[1]),
            'candidate_type': '道路段中点',
        })
        selected_positions.append(midpoint)

    return pd.DataFrame(candidate_records)

candidate_pool = build_candidate_pool(H, min_distance_px=55.0, max_candidates=520, random_seed=random_seed)
candidate_by_id = candidate_pool.set_index('candidate_id').to_dict(orient='index')
node_to_candidate_ids = defaultdict(list)
for _, row in candidate_pool.iterrows():
    node_to_candidate_ids[int(row['node'])].append(row['candidate_id'])

candidate_summary = candidate_pool['candidate_type'].value_counts().rename_axis('候选点类型').reset_index(name='数量')
display(candidate_summary)
print('候选点总数：', len(candidate_pool))""",
    "build-candidate-pool",
)

code(
    """fig, ax = plt.subplots(figsize=(8, 8))
ax.imshow(network_data['rgb_small'])
colors = {'路口/端点': '#e76f51', '道路段中点': '#2a9d8f'}
for candidate_type, group in candidate_pool.groupby('candidate_type'):
    ax.scatter(
        group['x'] * network_data['scale'],
        group['y'] * network_data['scale'],
        s=10,
        alpha=0.75,
        label=f'{candidate_type}({len(group)})',
        color=colors.get(candidate_type, '#4c78a8'),
    )
ax.set_title('候选打卡点池分布图')
ax.axis('off')
ax.legend(loc='lower left')
plt.tight_layout()
candidate_points_path = OUTPUT_DIR / 'e3_candidate_points.png'
plt.savefig(candidate_points_path, dpi=220, bbox_inches='tight')
plt.show()
print('候选点分布图已保存：', candidate_points_path)""",
    "plot-candidate-pool",
)

md(
    """## 7. Baseline 算法设计

为了证明改进算法的必要性，本文设置三个 baseline：

1. **完全随机生成**：从候选池中随机选 5 个点，调用 `plan_route_for_points` 检验可行性，不考虑拥挤度。
2. **可行性优先随机生成**：随机生成大量满足 3 条道路约束的 5 点组合，再随机选出 10 组，不主动降低路线重叠。
3. **贪心低聚集生成**：逐组生成，每次产生若干可行候选组，选择与已有路线共享道路段较少的一组。

Baseline 的作用是分别回答：约束是否困难、仅满足可行性是否足够、简单贪心能达到什么水平。""",
    "baseline-intro",
)

code(
    """def candidate_record(candidate_id):
    record = candidate_by_id[candidate_id].copy()
    record['candidate_id'] = candidate_id
    return record

def candidate_ids_to_points(candidate_ids):
    return [candidate_record(candidate_id) for candidate_id in candidate_ids]

def route_shared_edge_count(plan, edge_loads):
    return int(sum(1 for edge in plan['used_edges'] if edge_loads.get(edge, 0) > 0))

def route_max_edge_load_after(plan, edge_loads):
    if not plan['used_edges']:
        return 0
    return int(max(edge_loads.get(edge, 0) + 1 for edge in plan['used_edges']))

def repeated_point_penalty(candidate_ids, selected_coords, near_distance=120.0):
    if not selected_coords:
        return 0
    coords = candidate_pool.set_index('candidate_id').loc[list(candidate_ids), ['x', 'y']].to_numpy()
    previous = np.array(selected_coords)
    dists = np.linalg.norm(coords[:, None, :] - previous[None, :, :], axis=2)
    return int((dists.min(axis=1) < near_distance).sum())

def update_edge_loads(edge_loads, plan):
    for edge in plan['used_edges']:
        edge_loads[edge] += 1

def append_selected_coords(selected_coords, candidate_ids):
    coords = candidate_pool.set_index('candidate_id').loc[list(candidate_ids), ['x', 'y']].to_numpy()
    selected_coords.extend([tuple(row) for row in coords])

def group_record(algorithm, group_id, candidate_ids, plan, edge_loads_before, objective_value, runtime_sec=None):
    shared_edges = route_shared_edge_count(plan, edge_loads_before)
    max_load_after = route_max_edge_load_after(plan, edge_loads_before)
    ordered_ids = [candidate_ids[i] for i in plan['order']] if plan['feasible'] else []
    return {
        'algorithm': algorithm,
        'group_id': group_id,
        'candidate_ids': tuple(candidate_ids),
        'feasible': bool(plan['feasible']),
        'order': ' -> '.join(ordered_ids) if ordered_ids else '不可行',
        'total_distance': plan['total_distance'],
        'max_segment_count': plan['max_segment_count'],
        'max_pair_distance': plan['max_pair_distance'],
        'max_pair_time_min': plan['max_pair_distance'] * ASSUMED_M_PER_PIXEL / RUNNING_SPEED_M_PER_MIN if plan['feasible'] else np.inf,
        'used_edge_count': len(plan['used_edges']),
        'shared_edge_count': shared_edges,
        'max_edge_load': max_load_after,
        'objective_value': objective_value,
        'runtime_sec': runtime_sec,
        'edge_path': plan['edge_path'],
        'used_edges': plan['used_edges'],
    }

def random_local_candidate_group(rng, candidate_ids, max_hops=MAX_SEGMENT_COUNT, n_points=POINTS_PER_GROUP):
    candidate_ids = list(candidate_ids)
    candidate_set = set(candidate_ids)
    first_id = str(rng.choice(candidate_ids))
    chosen = [first_id]
    chosen_nodes = {candidate_by_id[first_id]['node']}
    current_node = int(candidate_by_id[first_id]['node'])

    for _ in range(n_points - 1):
        nearby_nodes = nx.single_source_shortest_path_length(H, current_node, cutoff=max_hops)
        options = []
        for node, hops in nearby_nodes.items():
            if not (1 <= hops <= max_hops):
                continue
            for candidate_id in node_to_candidate_ids.get(int(node), []):
                if candidate_id in candidate_set and candidate_id not in chosen and int(node) not in chosen_nodes:
                    options.append(candidate_id)
        if not options:
            return None
        next_id = str(rng.choice(options))
        chosen.append(next_id)
        chosen_nodes.add(int(candidate_by_id[next_id]['node']))
        current_node = int(candidate_by_id[next_id]['node'])
    return tuple(chosen)

def objective_value_for_plan(plan, candidate_ids, edge_loads, selected_coords, distance_norm, weights=None):
    weights = weights or {'w1': 1.0, 'w2': 5.0, 'w3': 10.0, 'w4': 3.0, 'w5': 1e6, 'w6': 0.8}
    if not plan['feasible']:
        return weights['w5']
    normalized_total_distance = plan['total_distance'] / distance_norm
    shared_edge_count = route_shared_edge_count(plan, edge_loads)
    max_edge_load = route_max_edge_load_after(plan, edge_loads)
    repeated_penalty = repeated_point_penalty(candidate_ids, selected_coords)
    return (
        weights['w1'] * normalized_total_distance
        + weights['w2'] * shared_edge_count
        + weights['w3'] * max_edge_load
        + weights['w4'] * repeated_penalty
        + weights.get('w6', 0.0) * len(plan['used_edges'])
    )

segment_edge_lengths = np.array([data['weight'] for _, _, data in H.edges(data=True)])
distance_norm = float(np.percentile(segment_edge_lengths, 75) * 12)
print('目标函数距离归一化尺度：', round(distance_norm, 2))""",
    "shared-helpers",
)

code(
    """def run_baseline_random(candidate_pool, n_groups=10, max_attempts=1500, seed=42):
    rng = np.random.default_rng(seed)
    start_time = perf_counter()
    records = []
    edge_loads = defaultdict(int)
    selected_coords = []
    distance_cache = {}
    candidate_ids = candidate_pool['candidate_id'].to_numpy()
    attempts = 0
    while len(records) < n_groups and attempts < max_attempts:
        attempts += 1
        group_ids = tuple(str(x) for x in rng.choice(candidate_ids, size=POINTS_PER_GROUP, replace=False))
        if len({candidate_by_id[x]['node'] for x in group_ids}) < POINTS_PER_GROUP:
            continue
        plan = plan_route_for_points(candidate_ids_to_points(group_ids), H, distance_cache=distance_cache)
        if not plan['feasible']:
            continue
        obj = objective_value_for_plan(plan, group_ids, edge_loads, selected_coords, distance_norm)
        before = edge_loads.copy()
        records.append(group_record('Baseline 1 完全随机', len(records) + 1, group_ids, plan, before, obj))
        update_edge_loads(edge_loads, plan)
        append_selected_coords(selected_coords, group_ids)
    runtime = perf_counter() - start_time
    return records, edge_loads, {'algorithm': 'Baseline 1 完全随机', 'attempts': attempts, 'runtime_sec': runtime}

def run_baseline_feasible_random(candidate_pool, n_groups=10, max_attempts=2500, seed=43):
    rng = np.random.default_rng(seed)
    start_time = perf_counter()
    feasible_candidates = []
    distance_cache = {}
    candidate_ids = candidate_pool['candidate_id'].to_numpy()
    attempts = 0
    while attempts < max_attempts and len(feasible_candidates) < max(80, n_groups * 8):
        attempts += 1
        group_ids = random_local_candidate_group(rng, candidate_ids)
        if group_ids is None:
            continue
        plan = plan_route_for_points(candidate_ids_to_points(group_ids), H, distance_cache=distance_cache)
        if plan['feasible']:
            feasible_candidates.append((group_ids, plan))
    rng.shuffle(feasible_candidates)
    records = []
    edge_loads = defaultdict(int)
    selected_coords = []
    for group_ids, plan in feasible_candidates[:n_groups]:
        obj = objective_value_for_plan(plan, group_ids, edge_loads, selected_coords, distance_norm)
        before = edge_loads.copy()
        records.append(group_record('Baseline 2 可行性优先随机', len(records) + 1, group_ids, plan, before, obj))
        update_edge_loads(edge_loads, plan)
        append_selected_coords(selected_coords, group_ids)
    runtime = perf_counter() - start_time
    return records, edge_loads, {'algorithm': 'Baseline 2 可行性优先随机', 'attempts': attempts, 'runtime_sec': runtime}

def run_baseline_greedy(candidate_pool, n_groups=10, batch_size=70, max_attempts_per_group=900, seed=44):
    rng = np.random.default_rng(seed)
    start_time = perf_counter()
    records = []
    edge_loads = defaultdict(int)
    selected_coords = []
    distance_cache = {}
    candidate_ids = candidate_pool['candidate_id'].to_numpy()
    attempts = 0
    for group_id in range(1, n_groups + 1):
        candidates = []
        local_attempts = 0
        while len(candidates) < batch_size and local_attempts < max_attempts_per_group:
            attempts += 1
            local_attempts += 1
            group_ids = random_local_candidate_group(rng, candidate_ids)
            if group_ids is None:
                continue
            plan = plan_route_for_points(candidate_ids_to_points(group_ids), H, distance_cache=distance_cache)
            if not plan['feasible']:
                continue
            shared = route_shared_edge_count(plan, edge_loads)
            candidates.append((shared, plan['total_distance'], group_ids, plan))
        if not candidates:
            continue
        candidates.sort(key=lambda item: (item[0], item[1]))
        _, _, group_ids, plan = candidates[0]
        obj = objective_value_for_plan(plan, group_ids, edge_loads, selected_coords, distance_norm)
        before = edge_loads.copy()
        records.append(group_record('Baseline 3 贪心低聚集', group_id, group_ids, plan, before, obj))
        update_edge_loads(edge_loads, plan)
        append_selected_coords(selected_coords, group_ids)
    runtime = perf_counter() - start_time
    return records, edge_loads, {'algorithm': 'Baseline 3 贪心低聚集', 'attempts': attempts, 'runtime_sec': runtime}

print('Baseline 算法已定义。')""",
    "baseline-functions",
)

md(
    """## 8. 改进算法设计

本文提出 `MultiObjectiveLowCongestionGenerator`。它以“候选点组”为个体，每个个体包含 5 个打卡点，并必须通过 `plan_route_for_points` 检验。

目标函数为：

```text
J = w1 * normalized_total_distance
  + w2 * shared_edge_count
  + w3 * max_edge_load
  + w4 * repeated_point_penalty
  + w5 * infeasible_penalty
```

算法采用“候选池采样 + Beam Search + 局部替换搜索”：每轮生成大量可行候选组，按目标函数保留前若干个，再对较优解尝试随机替换一个打卡点；若目标函数下降则接受。每生成一组后更新路段负载。""",
    "improved-intro",
)

code(
    """class MultiObjectiveLowCongestionGenerator:
    def __init__(
        self,
        candidate_pool,
        segment_graph,
        n_groups=10,
        beam_width=12,
        batch_size=90,
        local_search_steps=18,
        max_attempts_per_group=1400,
        seed=42,
        weights=None,
    ):
        self.candidate_pool = candidate_pool
        self.segment_graph = segment_graph
        self.n_groups = n_groups
        self.beam_width = beam_width
        self.batch_size = batch_size
        self.local_search_steps = local_search_steps
        self.max_attempts_per_group = max_attempts_per_group
        self.rng = np.random.default_rng(seed)
        self.weights = weights or {'w1': 1.0, 'w2': 5.0, 'w3': 10.0, 'w4': 3.0, 'w5': 1e6, 'w6': 0.8}
        self.distance_cache = {}
        self.edge_loads = defaultdict(int)
        self.selected_coords = []
        self.candidate_ids = candidate_pool['candidate_id'].to_numpy()
        self.convergence_history = []
        self.attempts = 0

    def score(self, group_ids, plan):
        return objective_value_for_plan(plan, group_ids, self.edge_loads, self.selected_coords, distance_norm, weights=self.weights)

    def random_feasible_candidate(self):
        group_ids = random_local_candidate_group(self.rng, self.candidate_ids)
        if group_ids is None:
            return None
        plan = plan_route_for_points(candidate_ids_to_points(group_ids), self.segment_graph, distance_cache=self.distance_cache)
        if not plan['feasible']:
            return None
        return {'candidate_ids': tuple(group_ids), 'plan': plan, 'objective': self.score(group_ids, plan)}

    def local_search(self, item, group_id):
        best = item
        for step in range(1, self.local_search_steps + 1):
            base_ids = list(best['candidate_ids'])
            replace_index = int(self.rng.integers(0, POINTS_PER_GROUP))
            base_nodes = {candidate_by_id[cid]['node'] for i, cid in enumerate(base_ids) if i != replace_index}
            anchor_node = int(candidate_by_id[base_ids[(replace_index - 1) % POINTS_PER_GROUP]]['node'])
            nearby_nodes = nx.single_source_shortest_path_length(self.segment_graph, anchor_node, cutoff=MAX_SEGMENT_COUNT)
            options = []
            for node, hops in nearby_nodes.items():
                if not (1 <= hops <= MAX_SEGMENT_COUNT):
                    continue
                if int(node) in base_nodes:
                    continue
                options.extend(node_to_candidate_ids.get(int(node), []))
            options = [cid for cid in options if cid not in base_ids]
            if not options:
                continue
            trial_ids = base_ids.copy()
            trial_ids[replace_index] = str(self.rng.choice(options))
            if len({candidate_by_id[cid]['node'] for cid in trial_ids}) < POINTS_PER_GROUP:
                continue
            plan = plan_route_for_points(candidate_ids_to_points(trial_ids), self.segment_graph, distance_cache=self.distance_cache)
            if not plan['feasible']:
                continue
            objective = self.score(tuple(trial_ids), plan)
            if objective < best['objective']:
                best = {'candidate_ids': tuple(trial_ids), 'plan': plan, 'objective': objective}
            self.convergence_history.append({'group_id': group_id, 'step': step, 'best_objective': best['objective']})
        return best

    def generate(self):
        records = []
        start_time = perf_counter()
        for group_id in range(1, self.n_groups + 1):
            pool = []
            local_attempts = 0
            while len(pool) < self.batch_size and local_attempts < self.max_attempts_per_group:
                self.attempts += 1
                local_attempts += 1
                item = self.random_feasible_candidate()
                if item is not None:
                    pool.append(item)
            if not pool:
                continue
            pool.sort(key=lambda item: item['objective'])
            beam = pool[:self.beam_width]
            improved = [self.local_search(item, group_id) for item in beam]
            improved.sort(key=lambda item: item['objective'])
            best = improved[0]
            before = self.edge_loads.copy()
            records.append(group_record('MultiObjectiveLowCongestion', group_id, best['candidate_ids'], best['plan'], before, best['objective']))
            update_edge_loads(self.edge_loads, best['plan'])
            append_selected_coords(self.selected_coords, best['candidate_ids'])
            self.convergence_history.append({'group_id': group_id, 'step': self.local_search_steps + 1, 'best_objective': best['objective']})
        runtime = perf_counter() - start_time
        metadata = {'algorithm': 'MultiObjectiveLowCongestion', 'attempts': self.attempts, 'runtime_sec': runtime}
        return records, self.edge_loads, metadata, pd.DataFrame(self.convergence_history)

print('多目标低聚集生成器已定义。')""",
    "improved-generator",
)

md(
    """## 9. 10 组新打卡点生成实验

本节运行 3 个 baseline 和 1 个改进算法，并把所有生成结果统一汇总到 `generated_groups_summary`。如果某个算法在限定尝试次数内无法生成 10 组，则记录成功组数和失败情况，不让程序崩溃。""",
    "experiment-intro",
)

code(
    """algorithm_outputs = []
metadata_records = []

b1_records, b1_loads, b1_meta = run_baseline_random(candidate_pool, n_groups=N_GROUPS, max_attempts=1500, seed=42)
algorithm_outputs.append((b1_meta['algorithm'], b1_records, b1_loads))
metadata_records.append(b1_meta)

b2_records, b2_loads, b2_meta = run_baseline_feasible_random(candidate_pool, n_groups=N_GROUPS, max_attempts=2500, seed=43)
algorithm_outputs.append((b2_meta['algorithm'], b2_records, b2_loads))
metadata_records.append(b2_meta)

b3_records, b3_loads, b3_meta = run_baseline_greedy(candidate_pool, n_groups=N_GROUPS, batch_size=70, seed=44)
algorithm_outputs.append((b3_meta['algorithm'], b3_records, b3_loads))
metadata_records.append(b3_meta)

generator = MultiObjectiveLowCongestionGenerator(candidate_pool, H, n_groups=N_GROUPS, beam_width=12, batch_size=90, local_search_steps=18, seed=42)
mo_records, mo_loads, mo_meta, convergence_df = generator.generate()
algorithm_outputs.append((mo_meta['algorithm'], mo_records, mo_loads))
metadata_records.append(mo_meta)

all_records = [record for _, records, _ in algorithm_outputs for record in records]
generated_groups_summary = pd.DataFrame(all_records)
csv_columns = [
    'algorithm', 'group_id', 'feasible', 'order', 'total_distance', 'max_segment_count',
    'max_pair_distance', 'max_pair_time_min', 'used_edge_count', 'shared_edge_count',
    'max_edge_load', 'objective_value', 'runtime_sec'
]
generated_groups_summary_csv = generated_groups_summary[csv_columns].copy()
generated_summary_path = OUTPUT_DIR / 'e3_generated_groups_summary.csv'
generated_groups_summary_csv.to_csv(generated_summary_path, index=False, encoding='utf-8-sig')

display(generated_groups_summary_csv.head(20).round(3))
print('生成结果已保存：', generated_summary_path)""",
    "run-generation-experiments",
)

md(
    """## 10. 算法性能对比与可视化

统一比较指标包括：可行率、平均总路程、平均最大相邻道路段数、3 条道路约束满足率、共享道路段数量、最大单路段负载、拥挤指数、平均运行时间和成功生成组数。拥挤指数定义为：

```text
sum(load_e^2)
```

其中 `load_e` 表示道路段 `e` 被多少组路线使用。平方惩罚可以更明显地反映局部路段被集中使用的问题。""",
    "comparison-intro",
)

code(
    """def congestion_index(edge_loads):
    return int(sum(load * load for load in edge_loads.values()))

def comparison_row(algorithm, records, edge_loads, metadata):
    df = pd.DataFrame(records)
    success_groups = len(df)
    feasible_count = int(df['feasible'].sum()) if success_groups else 0
    attempts = max(metadata.get('attempts', success_groups), 1)
    runtime = metadata.get('runtime_sec', np.nan)
    return {
        'algorithm': algorithm,
        'feasibility_rate': feasible_count / attempts,
        'avg_total_distance': df['total_distance'].replace(np.inf, np.nan).mean() if success_groups else np.nan,
        'avg_max_segment_count': df['max_segment_count'].replace(np.inf, np.nan).mean() if success_groups else np.nan,
        'constraint_satisfaction_rate': float((df['max_segment_count'] <= MAX_SEGMENT_COUNT).mean()) if success_groups else 0.0,
        'total_shared_edges': int(df['shared_edge_count'].sum()) if success_groups else 0,
        'avg_shared_edges': df['shared_edge_count'].mean() if success_groups else np.nan,
        'max_edge_load': max(edge_loads.values()) if edge_loads else 0,
        'congestion_index': congestion_index(edge_loads),
        'avg_runtime_sec': runtime / max(success_groups, 1),
        'success_groups': success_groups,
        'attempts': attempts,
        'runtime_sec': runtime,
    }

metadata_by_algorithm = {item['algorithm']: item for item in metadata_records}
comparison_rows = []
for algorithm, records, edge_loads in algorithm_outputs:
    comparison_rows.append(comparison_row(algorithm, records, edge_loads, metadata_by_algorithm[algorithm]))
algorithm_comparison_df = pd.DataFrame(comparison_rows)
comparison_path = OUTPUT_DIR / 'e3_algorithm_comparison.csv'
algorithm_comparison_df.to_csv(comparison_path, index=False, encoding='utf-8-sig')

display(algorithm_comparison_df.round(4))
print('算法对比结果已保存：', comparison_path)""",
    "build-comparison-df",
)

code(
    """metrics_to_plot = [
    ('avg_total_distance', '平均总路程'),
    ('total_shared_edges', '总共享道路段数'),
    ('max_edge_load', '最大道路段负载'),
    ('congestion_index', '拥挤指数'),
    ('avg_runtime_sec', '平均运行时间(s)'),
]
fig, axes = plt.subplots(1, len(metrics_to_plot), figsize=(22, 4.5))
plot_df = algorithm_comparison_df.copy()
for ax, (metric, title) in zip(axes, metrics_to_plot):
    ax.bar(plot_df['algorithm'], plot_df[metric], color='#4c78a8')
    ax.set_title(title)
    ax.tick_params(axis='x', rotation=75)
    ax.grid(axis='y', alpha=0.25)
plt.tight_layout()
comparison_fig_path = OUTPUT_DIR / 'e3_algorithm_comparison.png'
plt.savefig(comparison_fig_path, dpi=220, bbox_inches='tight')
plt.show()
print('算法性能对比图已保存：', comparison_fig_path)""",
    "plot-algorithm-comparison",
)

code(
    """def plot_records_routes(records, title, output_path, max_groups=10):
    fig, ax = plt.subplots(figsize=(9, 9))
    ax.imshow(network_data['rgb_small'])
    colors = plt.cm.tab10(np.linspace(0, 1, max(1, min(max_groups, len(records)))))
    for idx, record in enumerate(records[:max_groups]):
        geometry = route_pixel_geometry_from_edges(record['edge_path'])
        if len(geometry) == 0:
            continue
        ax.plot(geometry[:, 0] * network_data['scale'], geometry[:, 1] * network_data['scale'], linewidth=1.8, color=colors[idx % len(colors)], label=f'第{record[\"group_id\"]}组')
        ids = record['candidate_ids']
        pts = candidate_pool.set_index('candidate_id').loc[list(ids)]
        ax.scatter(pts['x'] * network_data['scale'], pts['y'] * network_data['scale'], s=24, color=colors[idx % len(colors)], edgecolor='white', zorder=5)
    ax.set_title(title)
    ax.axis('off')
    ax.legend(loc='lower left', fontsize=8, ncol=2)
    plt.tight_layout()
    plt.savefig(output_path, dpi=230, bbox_inches='tight')
    plt.show()
    print('路线叠加图已保存：', output_path)

v2_routes_path = OUTPUT_DIR / 'e3_v2_low_congestion_routes.png'
plot_records_routes(mo_records, '多目标低聚集算法生成的 10 组路线（相邻打卡点不超过 3 条道路）', v2_routes_path)""",
    "plot-v2-routes",
)

code(
    """def edge_load_line_collection(edge_loads, segment_graph, scale, min_width=0.25, max_width=4.0):
    segments = []
    loads = []
    widths = []
    max_load = max(edge_loads.values()) if edge_loads else 1
    for edge, load in edge_loads.items():
        if load <= 0:
            continue
        a, b = edge
        geometry_nodes = list(segment_graph.edges[a, b]['geometry'])
        coords = np.array([G.nodes[node]['pos'] for node in geometry_nodes]) * scale
        if len(coords) < 2:
            continue
        for p1, p2 in zip(coords[:-1], coords[1:]):
            segments.append([p1, p2])
            loads.append(load)
            widths.append(min_width + (max_width - min_width) * load / max_load)
    lc = LineCollection(segments, cmap='inferno', linewidths=widths, alpha=0.9)
    lc.set_array(np.array(loads) if loads else np.array([0]))
    return lc

baseline_heatmap_name = 'Baseline 3 贪心低聚集'
baseline_loads = dict(b3_loads)
improved_loads = dict(mo_loads)
fig, axes = plt.subplots(1, 2, figsize=(15, 7))
for ax, loads, title in [
    (axes[0], baseline_loads, baseline_heatmap_name),
    (axes[1], improved_loads, 'MultiObjectiveLowCongestion'),
]:
    ax.imshow(network_data['rgb_small'])
    lc = edge_load_line_collection(loads, H, network_data['scale'])
    ax.add_collection(lc)
    ax.set_title(f'{title}\\n道路段使用频率热力图')
    ax.axis('off')
    cbar = fig.colorbar(lc, ax=ax, fraction=0.046, pad=0.03)
    cbar.set_label('道路段使用次数')
plt.tight_layout()
heatmap_path = OUTPUT_DIR / 'e3_congestion_heatmap_comparison.png'
plt.savefig(heatmap_path, dpi=230, bbox_inches='tight')
plt.show()
print('拥挤热力对比图已保存：', heatmap_path)""",
    "plot-heatmap-comparison",
)

code(
    """if not convergence_df.empty:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    for group_id, group in convergence_df.groupby('group_id'):
        ax.plot(group['step'], group['best_objective'], marker='o', linewidth=1.4, label=f'第{group_id}组')
    ax.set_title('多目标低聚集算法局部搜索收敛曲线')
    ax.set_xlabel('局部搜索步数')
    ax.set_ylabel('当前最优目标函数 J')
    ax.grid(alpha=0.25)
    ax.legend(ncol=2, fontsize=8)
    plt.tight_layout()
    convergence_path = OUTPUT_DIR / 'e3_optimization_convergence.png'
    plt.savefig(convergence_path, dpi=220, bbox_inches='tight')
    plt.show()
    print('收敛曲线已保存：', convergence_path)
else:
    convergence_path = OUTPUT_DIR / 'e3_optimization_convergence.png'
    print('没有收敛历史，未生成收敛曲线。')""",
    "plot-convergence",
)

md(
    """## 11. 结论与不足

本节根据统一对比结果自动生成结论。重点关注：改进算法是否在保证 10 组打卡点可行的同时，降低共享道路段数、最大路段负载和拥挤指数。""",
    "conclusion-intro",
)

code(
    """def safe_metric(df, algorithm, metric):
    row = df[df['algorithm'] == algorithm]
    if row.empty:
        return np.nan
    return row.iloc[0][metric]

improved_name = 'MultiObjectiveLowCongestion'
strong_baseline_name = 'Baseline 3 贪心低聚集'
improved_success = int(safe_metric(algorithm_comparison_df, improved_name, 'success_groups'))
improved_constraint = safe_metric(algorithm_comparison_df, improved_name, 'constraint_satisfaction_rate')
improved_shared = safe_metric(algorithm_comparison_df, improved_name, 'total_shared_edges')
improved_max_load = safe_metric(algorithm_comparison_df, improved_name, 'max_edge_load')
improved_congestion = safe_metric(algorithm_comparison_df, improved_name, 'congestion_index')
base_shared = safe_metric(algorithm_comparison_df, strong_baseline_name, 'total_shared_edges')
base_max_load = safe_metric(algorithm_comparison_df, strong_baseline_name, 'max_edge_load')
base_congestion = safe_metric(algorithm_comparison_df, strong_baseline_name, 'congestion_index')

summary_text = f'''
实验结果表明，本文提出的多目标低聚集生成算法成功生成 {improved_success} 组新打卡点，约束满足率为 {improved_constraint:.1%}。
与较强 baseline“贪心低聚集生成”相比，改进算法的总共享道路段数为 {improved_shared:.0f}，baseline 为 {base_shared:.0f}；最大路段负载为 {improved_max_load:.0f}，baseline 为 {base_max_load:.0f}；拥挤指数为 {improved_congestion:.0f}，baseline 为 {base_congestion:.0f}。
若改进算法运行时间高于 baseline，这是为了同时考虑路线长度、共享道路段、最大路段负载和点位分散度所付出的计算代价。
综合可行性、路线分散性和拥挤控制效果，推荐使用 MultiObjectiveLowCongestion 作为校园跑步打卡点自动生成算法。
'''.strip()
print(summary_text)

output_files = [
    generated_summary_path,
    comparison_path,
    candidate_points_path,
    comparison_fig_path,
    v2_routes_path,
    heatmap_path,
    convergence_path,
    road_extraction_path,
]
print('\\n本实验生成文件：')
for path in output_files:
    print(path)""",
    "auto-conclusion-and-files",
)

notebook = {
    "cells": cells,
    "metadata": {
        "kernelspec": {"display_name": "base", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "pygments_lexer": "ipython3"},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

NB_PATH.write_text(json.dumps(notebook, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"rewritten {NB_PATH}")
print(f"cells: {len(cells)}")
