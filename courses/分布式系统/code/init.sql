-- 初始化分布式系统实验数据库
CREATE DATABASE IF NOT EXISTS distributed_sys DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE distributed_sys;

-- 创建学生基本成绩表
CREATE TABLE IF NOT EXISTS student (
    student_id VARCHAR(20) PRIMARY KEY COMMENT '学号',
    name VARCHAR(50) NOT NULL COMMENT '学生姓名',
    chinese_score DOUBLE COMMENT '语文成绩',
    math_score DOUBLE COMMENT '数学成绩',
    english_score DOUBLE COMMENT '英语成绩'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学生基本成绩表';

-- 清空旧数据 (以防重复运行)
TRUNCATE TABLE student;

-- 插入测试样例数据
INSERT INTO student (student_id, name, chinese_score, math_score, english_score) VALUES
('2023001', 'Alice', 90.0, 95.0, 88.0),
('2023002', 'Bob', 85.0, 80.0, 92.0);
