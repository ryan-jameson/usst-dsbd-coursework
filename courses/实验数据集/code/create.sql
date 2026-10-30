-- 创建数据库
CREATE DATABASE IF NOT EXISTS AuctionGameDB DEFAULT CHARSET utf8mb4;
USE AuctionGameDB;

-- 1. 游戏场次表 (Game_Sessions)
-- 用于记录每一局游戏的全局状态
CREATE TABLE game_sessions (
    session_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '游戏场次ID',
    start_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '开始时间',
    status ENUM('WAITING', 'ROUND_1', 'ROUND_2', 'ROUND_3', 'ROUND_4', 'FINISHED') DEFAULT 'WAITING' COMMENT '当前游戏状态'
);

-- 2. 队伍表 (Teams)
-- 记录玩家组的信息和资金
CREATE TABLE teams (
    team_id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL COMMENT '所属游戏场次',
    team_name VARCHAR(50) NOT NULL COMMENT '组名',
    balance DECIMAL(10, 2) DEFAULT 100.00 COMMENT '当前本金',
    FOREIGN KEY (session_id) REFERENCES game_sessions(session_id) ON DELETE CASCADE
);

-- 3. 玩家表 (Players)
-- 核心设计：通过 true_team_id 实现间谍逻辑
CREATE TABLE players (
    player_id INT AUTO_INCREMENT PRIMARY KEY,
    team_id INT NOT NULL COMMENT '当前所在的物理组',
    true_team_id INT NOT NULL COMMENT '真实效忠的组(用于间谍判定)',
    player_name VARCHAR(50) NOT NULL,
    is_spy BOOLEAN DEFAULT FALSE COMMENT '是否是间谍标记',
    has_acted_this_round BOOLEAN DEFAULT FALSE COMMENT '本轮是否已行动(每人限一次)',
    FOREIGN KEY (team_id) REFERENCES teams(team_id),
    FOREIGN KEY (true_team_id) REFERENCES teams(team_id)
);

-- 4. 藏品表 (Items)
-- 记录藏品属性和状态
CREATE TABLE items (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL,
    item_code CHAR(1) NOT NULL COMMENT '藏品代号 A-H',
    item_name VARCHAR(100) COMMENT '藏品名称',
    base_price DECIMAL(10, 2) NOT NULL COMMENT '起拍价格',
    current_value DECIMAL(10, 2) NOT NULL COMMENT '当前价值(初始价值)',
    increment_coeff DECIMAL(5, 2) DEFAULT 1.5 COMMENT '增量系数(冲突时价值提升倍数)',
    owner_team_id INT DEFAULT NULL COMMENT '归属队伍，NULL为未被拍下',
    status ENUM('AVAILABLE', 'SOLD', 'CONFLICT_LOCKED') DEFAULT 'AVAILABLE',
    FOREIGN KEY (session_id) REFERENCES game_sessions(session_id),
    FOREIGN KEY (owner_team_id) REFERENCES teams(team_id)
);

-- 5. 竞拍记录表 (Bids)
-- 记录所有出价行为，用于结算
CREATE TABLE bids (
    bid_id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL,
    round_num INT NOT NULL COMMENT '轮次: 1-4',
    phase_type ENUM('INITIAL', 'DUEL') DEFAULT 'INITIAL' COMMENT '出价阶段：初始出价或冲突对决',
    item_id INT NOT NULL,
    team_id INT NOT NULL COMMENT '名义出价组',
    player_id INT NOT NULL COMMENT '实际操作人',
    bid_amount DECIMAL(10, 2) NOT NULL,
    bid_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES game_sessions(session_id),
    FOREIGN KEY (item_id) REFERENCES items(item_id),
    FOREIGN KEY (team_id) REFERENCES teams(team_id),
    FOREIGN KEY (player_id) REFERENCES players(player_id)
);