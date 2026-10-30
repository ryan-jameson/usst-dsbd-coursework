import numpy as np
import csv

matrix = np.arange(25).reshape((5, 5)) 
print("第一题矩阵")
print(matrix)

vector = np.random.rand(50) 
mean_value = np.mean(vector) 
print("\n随机数平均值:", mean_value)

boundary_matrix = np.ones((5, 5)) 
boundary_matrix[1:-1, 1:-1] = 0 
print("\n以1为边的矩阵")
print(boundary_matrix)

random_array = np.random.rand(10) 
sorted_array = np.sort(random_array) #从小到大排序
print("\n随机数排序数组:")
print(sorted_array)

def fibonacci(n):
    a, b = 1, 1
    for _ in range(n):
        yield a 
        a, b = b, a + b
fib_sequence = list(fibonacci(10))  # 获取前10个斐波那契数
print("\n斐波那契数列前十项:")
print(fib_sequence)

def recursive_power(x, n):
    if n == 0:
        return 1
    else:
        return x * recursive_power(x, n - 1) #递归

def iterative_power(x, n):
    result = 1
    for _ in range(n):
        result *= x
    return result #非递归

x = 2  # 示例值
n = 5  # 示例值
print(f"\n递归算法求2的5次方:", recursive_power(x, n))
print(f"非递归算法求2的5次方:", iterative_power(x, n))

data = [
    ['姓名', '年龄', '职业', '工资'],
    ['张三', 20, '销售员', 5000],
    ['李四', 22, '程序员', 8000],
    ['王五', 24, '程序员', 8500],
    ['赵六', 21, '经理', 9800]
]


with open('employees.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerows(data)


salaries = []
with open('employees.csv', 'r', encoding='utf-8') as file:
    reader = csv.reader(file)
    next(reader)  # 跳过标题行
    for row in reader:
        salaries.append(int(row[3])) 

# 计算工资的最大值、最小值、均值
max_salary = max(salaries)
min_salary = min(salaries)
avg_salary = sum(salaries)/len(salaries) #也可以用np.mean

print(f"\n最高工资: {max_salary}")
print(f"最小工资: {min_salary}")
print(f"平均工资: {avg_salary}")