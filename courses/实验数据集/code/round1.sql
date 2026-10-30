-- ==========================================
-- 0. 环境准备 (确保变量存在)
-- ==========================================
SELECT session_id INTO @s_id FROM game_sessions ORDER BY session_id DESC LIMIT 1;
-- 重新绑定队伍变量
SELECT team_id INTO @t1 FROM teams WHERE team_name='Team_A' AND session_id=@s_id;
SELECT team_id INTO @t2 FROM teams WHERE team_name='Team_B' AND session_id=@s_id;
SELECT team_id INTO @t3 FROM teams WHERE team_name='Team_C' AND session_id=@s_id;
SELECT team_id INTO @t4 FROM teams WHERE team_name='Team_D' AND session_id=@s_id;
SELECT team_id INTO @t5 FROM teams WHERE team_name='Team_E' AND session_id=@s_id;
SELECT team_id INTO @t6 FROM teams WHERE team_name='Team_F' AND session_id=@s_id;
-- 藏品变量
SELECT item_id INTO @iA FROM items WHERE item_code='A' AND session_id=@s_id;
SELECT item_id INTO @iC FROM items WHERE item_code='C' AND session_id=@s_id;
SELECT item_id INTO @iE FROM items WHERE item_code='E' AND session_id=@s_id;
SELECT item_id INTO @iG FROM items WHERE item_code='G' AND session_id=@s_id;

UPDATE game_sessions SET status='ROUND_1' WHERE session_id=@s_id;

-- ==========================================
-- 1. 第一轮出价 (Round 1 Bidding)
-- ==========================================

-- [A组] 独具慧眼，单吊 藏品A (起拍 70)
-- 只有 A组 出价
INSERT INTO bids (session_id, round_num, phase_type, item_id, team_id, player_id, bid_amount) 
SELECT @s_id, 1, 'INITIAL', @iA, @t1, player_id, 75 FROM players WHERE team_id=@t1 LIMIT 1;

-- [B组 与 C组] 争夺 藏品C (起拍 50)
-- B组 出价 55
INSERT INTO bids (session_id, round_num, phase_type, item_id, team_id, player_id, bid_amount) 
SELECT @s_id, 1, 'INITIAL', @iC, @t2, player_id, 55 FROM players WHERE team_id=@t2 LIMIT 1;
-- C组 出价 60 (更高)
INSERT INTO bids (session_id, round_num, phase_type, item_id, team_id, player_id, bid_amount) 
SELECT @s_id, 1, 'INITIAL', @iC, @t3, player_id, 60 FROM players WHERE team_id=@t3 LIMIT 1;

-- [D组、E组、F组] 混战 藏品E (起拍 40) -> 3组撞车
INSERT INTO bids (session_id, round_num, phase_type, item_id, team_id, player_id, bid_amount) VALUES
(@s_id, 1, 'INITIAL', @iE, @t4, (SELECT player_id FROM players WHERE team_id=@t4 LIMIT 1), 45),
(@s_id, 1, 'INITIAL', @iE, @t5, (SELECT player_id FROM players WHERE team_id=@t5 LIMIT 1), 50),
(@s_id, 1, 'INITIAL', @iE, @t6, (SELECT player_id FROM players WHERE team_id=@t6 LIMIT 1), 42);

-- ==========================================
-- 2. 第一轮 结算 (Round 1 Settlement)
-- ==========================================

-- [结算 A] 1组出价，以起拍价 70 成交
-- 规则：若仅1组出价，以起拍价获得
UPDATE teams SET balance = balance - 70 WHERE team_id = @t1;
UPDATE items SET owner_team_id = @t1, status = 'SOLD' WHERE item_id = @iA;

-- [结算 C] 2组出价 -> 触发 DUEL -> C组获胜
-- 模拟对决：C组(T3)初始出价高，占据主动，最终出价 65 拿下
-- 插入对决出价记录
INSERT INTO bids (session_id, round_num, phase_type, item_id, team_id, player_id, bid_amount) 
SELECT @s_id, 1, 'DUEL', @iC, @t3, player_id, 65 FROM players WHERE team_id=@t3 AND has_acted_this_round=0 LIMIT 1;
INSERT INTO bids (session_id, round_num, phase_type, item_id, team_id, player_id, bid_amount) 
SELECT @s_id, 1, 'DUEL', @iC, @t2, player_id, 62 FROM players WHERE team_id=@t2 AND has_acted_this_round=0 LIMIT 1;

-- C组扣费 65 (对决获胜按最终出价算)
UPDATE teams SET balance = balance - 65 WHERE team_id = @t3;
UPDATE items SET owner_team_id = @t3, status = 'SOLD' WHERE item_id = @iC;

-- [结算 E] 3组出价 -> 冲突无效 -> 藏品保留
-- 仅更新状态，物品仍在
UPDATE items SET status = 'AVAILABLE' WHERE item_id = @iE;

-- ==========================================
-- 3. 第一轮 价值核算 (Value Calculation)
-- ==========================================
-- 规则：当前价值 = 初始价值 + (本轮竞拍人数 * 系数)
-- A (20系数): T1参与 -> 100 + 1*20 = 120
-- C (30系数): T2, T3参与 -> 80 + 2*30 = 140
-- E (10系数): T4, T5, T6参与 -> 80 + 3*10 = 110
UPDATE items i
JOIN (
    SELECT item_id, COUNT(DISTINCT team_id) as team_count
    FROM bids 
    WHERE session_id = @s_id AND round_num = 1
    GROUP BY item_id
) b ON i.item_id = b.item_id
SET i.current_value = i.current_value + (b.team_count * i.increment_coeff);
-- 最终结果查看
SELECT 
    t.team_name, 
    t.balance as '剩余本金', 
    GROUP_CONCAT(i.item_code ORDER BY i.item_code) as '拥有藏品',
    SUM(IFNULL(i.current_value, 0)) as '藏品总价值',
    (t.balance + IFNULL(SUM(i.current_value), 0)) as '总成绩(参考)'
FROM teams t 
LEFT JOIN items i ON t.team_id = i.owner_team_id
WHERE t.session_id = @s_id
GROUP BY t.team_id
ORDER BY team_name;