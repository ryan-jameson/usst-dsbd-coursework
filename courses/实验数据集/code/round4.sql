-- ==========================================
-- 1. 第四轮 环境准备
-- ==========================================
SELECT session_id INTO @s_id FROM game_sessions ORDER BY session_id DESC LIMIT 1;
-- 队伍 ID
SELECT team_id INTO @t1 FROM teams WHERE team_name='Team_A' AND session_id=@s_id; -- A
SELECT team_id INTO @t2 FROM teams WHERE team_name='Team_B' AND session_id=@s_id; -- B
SELECT team_id INTO @t4 FROM teams WHERE team_name='Team_D' AND session_id=@s_id; -- D
SELECT team_id INTO @t6 FROM teams WHERE team_name='Team_F' AND session_id=@s_id; -- F
-- 藏品 ID
SELECT item_id INTO @iG FROM items WHERE item_code='G' AND session_id=@s_id;

UPDATE game_sessions SET status='ROUND_4' WHERE session_id=@s_id;

-- ==========================================
-- 2. 第四轮 出价 (Final Showdown)
-- ==========================================
-- A组：卧底不操作 -> 无 INSERT
-- D组：卧底不操作 -> 无 INSERT

-- [B组] 派出 USER1，对 G 出价 (初步试探，比如出价 30)
INSERT INTO bids (session_id, round_num, phase_type, item_id, team_id, player_id, bid_amount) 
SELECT @s_id, 4, 'INITIAL', @iG, @t2, player_id, 30 
FROM players WHERE team_id=@t2 AND player_name='B_User1' LIMIT 1;

-- [F组] 派出 USER1，对 G 出价 (梭哈，出价 40)
INSERT INTO bids (session_id, round_num, phase_type, item_id, team_id, player_id, bid_amount) 
SELECT @s_id, 4, 'INITIAL', @iG, @t6, player_id, 40 
FROM players WHERE team_id=@t6 AND player_name='F_User1' LIMIT 1;

-- ==========================================
-- 3. 第四轮 结算 (Settlement)
-- ==========================================
-- 触发对决 (B vs F)

-- B组看到 F 只能出40，于是出价 50 绝杀
INSERT INTO bids (session_id, round_num, phase_type, item_id, team_id, player_id, bid_amount) 
SELECT @s_id, 4, 'DUEL', @iG, @t2, player_id, 50 
FROM players WHERE team_id=@t2 AND player_name='B_User1' LIMIT 1;

-- F组已经没钱加价了，无法继续出价 (或者出价无效)，这里不插入 F 的 DUEL 记录，或者插入一个放弃的记录

-- 结果：B 组获胜
UPDATE teams SET balance = balance - 50 WHERE team_id = @t2;
UPDATE items SET owner_team_id = @t2, status = 'SOLD' WHERE item_id = @iG;

-- ==========================================
-- 4. 第四轮 价值更新
-- ==========================================
-- G (系数30): 参与组 B, F (2个组) -> 价值 + 60
-- 注意：此时 G 已经经历过第一轮(2人)、第三轮(3人)的洗礼，基础很高。
UPDATE items i
JOIN (
    SELECT item_id, COUNT(DISTINCT team_id) as team_count
    FROM bids 
    WHERE session_id = @s_id AND round_num = 4
    GROUP BY item_id
) b ON i.item_id = b.item_id
SET i.current_value = i.current_value + (b.team_count * i.increment_coeff);

UPDATE game_sessions SET status='FINISHED' WHERE session_id=@s_id;

-- ==========================================
-- 5. 最终大结算 (Final Leaderboard)
-- ==========================================

-- 5.1 查看所有藏品的最终价值
SELECT 
    item_code, 
    item_name, 
    current_value as '最终价值',
    increment_coeff as '增值系数',
    (SELECT team_name FROM teams WHERE team_id = items.owner_team_id) as '最终归属'
FROM items 
WHERE session_id = @s_id
ORDER BY item_code;

-- 如果视图已存在则替换，不存在则创建
CREATE OR REPLACE VIEW view_game_results AS
SELECT 
    t.session_id,
    -- 使用窗口函数计算排名，按场次分组(PARTITION)，按总分降序
    RANK() OVER (
        PARTITION BY t.session_id 
        ORDER BY (t.balance + IFNULL(SUM(i.current_value), 0)) DESC, t.balance DESC
    ) as ranking,
    t.team_name,
    t.balance as remaining_balance,
    -- 拼接该组拥有的藏品代码，若无则显示'无'
    IFNULL(GROUP_CONCAT(i.item_code ORDER BY i.item_code SEPARATOR ','), '无') as items_owned,
    -- 计算藏品总价值，若无藏品则为0
    IFNULL(SUM(i.current_value), 0) as items_total_value,
    -- 计算总成绩 = 余额 + 藏品价值
    (t.balance + IFNULL(SUM(i.current_value), 0)) as total_score
FROM teams t
LEFT JOIN items i ON t.team_id = i.owner_team_id
GROUP BY t.session_id, t.team_id;

-- ==========================================
-- 5. 最终大结算 (使用视图)
-- ==========================================

-- 只需要指定当前的 session_id 即可
SELECT 
    ranking as '名次',
    team_name as '队伍',
    remaining_balance as '剩余资金',
    items_owned as '获得藏品',
    items_total_value as '藏品总价值',
    total_score as '总成绩'
FROM view_game_results
WHERE session_id = @s_id
ORDER BY ranking ASC;