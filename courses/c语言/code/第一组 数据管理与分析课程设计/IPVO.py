import numpy as np
from PIL import Image
import math
import matplotlib.pyplot as plt

# ===================== 基础工具函数 =====================
def load_gray(path):
    """读取灰度图像，返回uint8数组"""
    return np.array(Image.open(path).convert('L'), dtype=np.uint8)

def psnr(img1, img2):
    """计算峰值信噪比（评估图像质量）"""
    img1 = img1.astype(np.float64); img2 = img2.astype(np.float64)
    mse = np.mean((img1 - img2) **2)
    return 99.0 if mse == 0 else 20 * math.log10(255.0 / math.sqrt(mse))

# ===================== IPVO核心算法 =====================
def embed_ipvo(img_uint8, payload_bits, block_size=3, threshold=2):
    """IPVO嵌入算法（单一层）"""
    X = img_uint8.astype(np.int16)
    H, W = X.shape
    stego = X.copy()
    payload = np.array(payload_bits, dtype=np.uint8)
    ptr, used = 0, 0  # 载荷指针与实际嵌入数

    # 计算预测误差
    pred_error = np.zeros_like(X, dtype=np.int16)
    half = block_size // 2
    for y in range(H):
        for x in range(W):
            neighbors = []
            for dy in range(-half, half + 1):
                for dx in range(-half, half + 1):
                    if dy == 0 and dx == 0:
                        continue  # 排除自身
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < H and 0 <= xx < W:
                        neighbors.append(X[yy, xx])
            pred = np.mean(neighbors) if neighbors else X[y, x]
            pred_error[y, x] = X[y, x] - pred

    # 记录嵌入信息
    embed_info = []
    # 遍历所有像素块
    for y in range(half, H - half):
        for x in range(half, W - half):
            if ptr >= len(payload):
                break  # 载荷嵌入完毕

            # 提取当前块并排序
            block = []
            coords = []
            for dy in range(-half, half + 1):
                for dx in range(-half, half + 1):
                    yy, xx = y + dy, x + dx
                    block.append((X[yy, xx], yy, xx))
            sorted_block = sorted(block, key=lambda x: x[0])
            sorted_vals = [p[0] for p in sorted_block]
            coords = [p[1:] for p in sorted_block]

            # 动态区间划分
            min_val, max_val = sorted_vals[0], sorted_vals[-1]
            safe_indices = [i for i in range(1, len(sorted_vals)-1) 
                          if (sorted_vals[i] - min_val > threshold and 
                              max_val - sorted_vals[i] > threshold)]
            
            if not safe_indices:
                continue

            # 选择最佳嵌入像素
            safe_pixels = [(i, coords[i], sorted_vals[i]) for i in safe_indices]
            safe_pixels.sort(key=lambda p: abs(pred_error[p[1][0], p[1][1]]))
            best_idx, best_coord, best_val = safe_pixels[0]

            # 嵌入比特
            bit = payload[ptr]
            yy, xx = best_coord
            if bit == 1:
                new_val = best_val + 1
            else:
                new_val = best_val - 1

            # 验证新值
            if (new_val - min_val > threshold and max_val - new_val > threshold and
                0 <= new_val <= 255):
                stego[yy, xx] = new_val
                used += 1
                ptr += 1
                embed_info.append({
                    "coord": (yy, xx),
                    "bit": bit,
                    "original_val": best_val
                })

    info = {
        "block_size": block_size,
        "threshold": threshold,
        "used": used,  # 当前层实际嵌入的比特数
        "embed_info": embed_info,
        "H": H,
        "W": W
    }
    return stego.astype(np.uint8), info

def extract_ipvo(stego_uint8, info):
    """IPVO提取算法（单一层）"""
    Y = stego_uint8.astype(np.int16)
    recovered = Y.copy()
    bits = []
    embed_info = info["embed_info"]

    # 提取比特并恢复原始值
    for item in embed_info:
        yy, xx = item["coord"]
        original_val = item["original_val"]
        recovered[yy, xx] = original_val
        bits.append(item["bit"])

    return recovered.astype(np.uint8), np.array(bits, dtype=np.uint8)

# ===================== 多层IPVO封装 =====================
def multi_ipvo_embed(img, payload_bits, layers=2, block_sizes=None, thresholds=None):
    """
    多层IPVO嵌入
    - layers: 嵌入层数
    - block_sizes: 每层的块大小（如[3,5]，默认逐层增大）
    - thresholds: 每层的安全阈值（如[2,1]，默认相同）
    返回：隐写图像、所有层的元数据、每层嵌入量
    """
    stego = img.copy()
    remaining_bits = list(payload_bits)  # 剩余待嵌入的比特
    all_metas = []  # 存储每层的元数据
    capacities = []  # 存储每层实际嵌入的比特数

    # 默认参数：块大小逐层增大，阈值保持不变
    if block_sizes is None:
        block_sizes = [3 + 2*i for i in range(layers)]  # [3,5,7...]
    if thresholds is None:
        thresholds = [2]*layers  # 所有层阈值为2

    for layer in range(layers):
        if not remaining_bits:
            # 载荷已嵌入完毕，后续层不嵌入
            all_metas.append(None)
            capacities.append(0)
            continue

        # 当前层参数
        block_size = block_sizes[layer]
        threshold = thresholds[layer]

        # 嵌入当前层
        stego, meta = embed_ipvo(
            stego, 
            remaining_bits, 
            block_size=block_size, 
            threshold=threshold
        )

        # 记录当前层信息
        used = meta["used"]
        all_metas.append(meta)
        capacities.append(used)

        # 更新剩余比特
        remaining_bits = remaining_bits[used:]
        print(f"[LAYER {layer+1}] 嵌入比特数={used}, 剩余比特数={len(remaining_bits)}")

    return stego, all_metas, capacities

def multi_ipvo_extract(stego, all_metas):
    """多层IPVO提取（逆序提取）"""
    rec = stego.copy()
    all_bits = []  # 存储所有提取的比特

    # 从最后一层开始逆向提取
    for layer in reversed(range(len(all_metas))):
        meta = all_metas[layer]
        if meta is None:
            # 空层，无比特提取
            continue

        # 提取当前层并恢复图像
        rec, extracted_bits = extract_ipvo(rec, meta)
        all_bits = list(extracted_bits) + all_bits  # 保持原始顺序
        print(f"[EXTRACT LAYER {layer+1}] 提取比特数={len(extracted_bits)}")

    return rec, np.array(all_bits, dtype=np.uint8)
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm  # 导入字体管理模块
# 设置中文字体
font_path = "/home/USER/anaconda3/envs/test/lib/python3.10/site-packages/matplotlib/mpl-data/fonts/ttf/simhei.ttf"  # 替换为实际字体路径
# 手动加载字体
custom_font = fm.FontProperties(fname=font_path)
font_name = custom_font.get_name()  # 如 'SimHei'

# 将字体加入 Matplotlib 的字体管理器
fm.fontManager.addfont(font_path)
plt.rcParams['font.family'] = font_name  # 使用字体名称
plt.rcParams['axes.unicode_minus'] = False  # 正常显示负号
import matplotlib.pyplot as plt
img_path = '/mnt/e/平时作业/c语言/plane.tif'
# ===================== 实验验证 =====================
if __name__ == "__main__":
    img = load_gray(img_path)
    print(f"原始图像形状：{img.shape}")

    # 生成测试载荷（根据图像大小调整，避免过大）
    np.random.seed(2025)
    payload = np.random.randint(0, 2, size=600000, dtype=np.uint8)  # 600kb比特
    print(f"待嵌入载荷长度：{len(payload)} bits")

    # 多层IPVO嵌入（3层，不同块大小）
    layers = 3
    stego, all_metas, capacities = multi_ipvo_embed(
        img, 
        payload, 
        layers=layers,
        block_sizes=[9,9,9],  # 块大小逐层增大（利用更多冗余）
        thresholds=[1,1,1]    # 阈值可适当减小以增加容量
    )

    # 多层IPVO提取
    recovered, extracted_bits = multi_ipvo_extract(stego, all_metas)

    # 计算总嵌入比特数
    total_used = sum(capacities)
    print(f"\n总嵌入比特数：{total_used}")

    # 验证结果
    is_reversible = np.array_equal(recovered, img)
    is_payload_match = np.array_equal(extracted_bits, payload[:total_used])
    
    print(f"图像可逆性：{'成功' if is_reversible else '失败'}")
    print(f"载荷一致性：{'成功' if is_payload_match else '失败'}")
    print(f"隐写图像PSNR：{psnr(img, stego):.2f} dB")

    # 可视化
    plt.figure(figsize=(15, 5))
    plt.subplot(131); plt.imshow(img, cmap='gray'); plt.title("原始图像")
    plt.subplot(132); plt.imshow(stego, cmap='gray'); plt.title("多层IPVO隐写图像")
    plt.subplot(133); plt.imshow(recovered, cmap='gray'); plt.title("恢复图像")
    plt.tight_layout(); plt.show()
def serialize_metas(all_metas):
    """将嵌入信息序列化为字节串"""
    return pickle.dumps(all_metas)

def deserialize_metas(byte_data):
    """将字节串反序列化为嵌入信息"""
    return pickle.loads(byte_data)
import struct

def save_as_custom_file(stego_img, all_metas, output_path):
    """将隐写图像和元数据保存为自定义文件"""
    # 序列化元数据
    meta_bytes = serialize_metas(all_metas)
    meta_size = len(meta_bytes)
    
    # 打开文件写入
    with open(output_path, 'wb') as f:
        # 写入文件标识
        f.write(b'MYRDH')
        # 写入元数据大小 (4字节无符号整数)
        f.write(struct.pack('I', meta_size))
        # 写入元数据
        f.write(meta_bytes)
        # 写入图像数据 (直接写入原始字节)
        f.write(stego_img.tobytes())

    print(f"✅ 自定义文件已保存: {output_path}")

def load_from_custom_file(input_path):
    """从自定义文件中加载隐写图像和元数据"""
    with open(input_path, 'rb') as f:
        # 读取并验证文件标识
        header = f.read(5)
        if header != b'MYRDH':
            raise ValueError("无效的文件格式")
        
        # 读取元数据大小
        meta_size = struct.unpack('I', f.read(4))[0]
        # 读取元数据
        meta_bytes = f.read(meta_size)
        all_metas = deserialize_metas(meta_bytes)
        
        # 读取剩余的图像数据
        img_data = f.read()
        # 重建图像 (假设是512x512灰度图，您需要根据实际情况调整)
        stego_img = np.frombuffer(img_data, dtype=np.uint8).reshape((512, 512))
    
    return stego_img, all_metas
save_as_custom_file(stego, all_metas, '/mnt/e/平时作业/c语言/plane_hide.tif')
stego,all_metas=load_from_custom_file('/mnt/e/平时作业/c语言/plane_hide.tif')
recovered, extracted_bits = multi_ipvo_extract(stego, all_metas)

    # 验证结果
is_reversible = np.array_equal(recovered, img)
is_payload_match = np.array_equal(extracted_bits, payload[:total_used])
    
print(f"图像可逆性：{'成功' if is_reversible else '失败'}")
print(f"载荷一致性：{'成功' if is_payload_match else '失败'}")
print(f"隐写图像PSNR：{psnr(img, stego):.2f} dB")