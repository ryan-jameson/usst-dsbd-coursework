Use auctiongamedb;
-- ==========================================
-- 4. 第二轮 准备
-- ==========================================
SELECT item_id INTO @iB FROM items WHERE item_code='B' AND session_id=@s_id;
SELECT item_id INTO @iD FROM items WHERE item_code='D' AND session_id=@s_id;
SELECT item_id INTO @iF FROM items WHERE item_code='F' AND session_id=@s_id;
SELECT item_id INTO @iH FROM items WHERE item_code='H' AND session_id=@s_id;

UPDATE game_sessions SET status='ROUND_2' WHERE session_id=@s_id;

-- ==========================================
-- 5. 第二轮 出价 (Round 2 Bidding)
-- ==========================================

-- [A组 T1] 余额30 -> 抢 H (起拍10)
INSERT INTO bids (session_id, round_num, phase_type, item_id, team_id, player_id, bid_amount) 
SELECT @s_id, 2, 'INITIAL', @iH, @t1, player_id, 15 FROM players WHERE team_id=@t1 LIMIT 1;

-- [C组 T3] 余额35 -> 抢 F (起拍30)
INSERT INTO bids (session_id, round_num, phase_type, item_id, team_id, player_id, bid_amount) 
SELECT @s_id, 2, 'INITIAL', @iF, @t3, player_id, 32 FROM players WHERE team_id=@t3 LIMIT 1;

-- [D组 T4] 余额100 -> 抢 D (起拍40) - 捡漏
INSERT INTO bids (session_id, round_num, phase_type, item_id, team_id, player_id, bid_amount) 
SELECT @s_id, 2, 'INITIAL', @iD, @t4, player_id, 45 FROM players WHERE team_id=@t4 LIMIT 1;

-- [E组 T5 vs F组 T6] 争夺高价 B (起拍70)
-- T5 正常出价 80
INSERT INTO bids (session_id, round_num, phase_type, item_id, team_id, player_id, bid_amount) 
SELECT @s_id, 2, 'INITIAL', @iB, @t5, player_id, 80 
FROM players WHERE team_id=@t5 AND is_spy=0 LIMIT 1;

-- [卧底时刻!] T6 出价 80 (造成平局)
-- 操作者是 F_Spy_from_E (T5派到T6的卧底)
-- 他的目的是让 T6 卷入价格战，消耗 T6 资金，或者在对决中故意输掉/抬价
INSERT INTO bids (session_id, round_num, phase_type, item_id, team_id, player_id, bid_amount) 
SELECT @s_id, 2, 'INITIAL', @iB, @t6, player_id, 80 
FROM players WHERE team_id=@t6 AND is_spy=1 LIMIT 1; 

-- ==========================================
-- 6. 第二轮 结算 (Round 2 Settlement)
-- ==========================================

-- [结算 H] T1 获胜
UPDATE teams SET balance = balance - 10 WHERE team_id = @t1; -- 单人出价按起拍价
UPDATE items SET owner_team_id = @t1, status = 'SOLD' WHERE item_id = @iH;

-- [结算 F] T3 获胜
UPDATE teams SET balance = balance - 30 WHERE team_id = @t3; -- 单人出价按起拍价
UPDATE items SET owner_team_id = @t3, status = 'SOLD' WHERE item_id = @iF;

-- [结算 D] T4 获胜
UPDATE teams SET balance = balance - 40 WHERE team_id = @t4; -- 单人出价按起拍价
UPDATE items SET owner_team_id = @t4, status = 'SOLD' WHERE item_id = @iD;

-- [结算 B] T5 vs T6 -> 对决
-- 卧底既然已经让 T6 入局，现在 T5 决定以高价拿下，或者 T6 卧底故意乱出价
-- 假设 T5 决心拿下，出价 90
INSERT INTO bids (session_id, round_num, phase_type, item_id, team_id, player_id, bid_amount) 
SELECT @s_id, 2, 'DUEL', @iB, @t5, player_id, 90 FROM players WHERE team_id=@t5 AND has_acted_this_round=0 LIMIT 1;

-- T6 (卧底) 放弃抵抗或出低价，让 T5 赢，但已经把 T6 的机会浪费了
INSERT INTO bids (session_id, round_num, phase_type, item_id, team_id, player_id, bid_amount) 
SELECT @s_id, 2, 'DUEL', @iB, @t6, player_id, 85 FROM players WHERE team_id=@t6 AND has_acted_this_round=0 LIMIT 1;

-- T5 获胜，扣除 90
UPDATE teams SET balance = balance - 90 WHERE team_id = @t5;
UPDATE items SET owner_team_id = @t5, status = 'SOLD' WHERE item_id = @iB;

-- ==========================================
-- 7. 第二轮 价值核算 & 结果展示
-- ==========================================
-- B (10系数): T5, T6参与 -> 初始110 + 2*10 = 130
-- F (15系数): T3参与 -> 初始40 + 1*15 = 55
-- H (5系数): T1参与 -> 初始50 + 1*5 = 55
-- D (20系数): T4参与 -> 初始40 + 1*20 = 60

UPDATE items i
JOIN (
    SELECT item_id, COUNT(DISTINCT team_id) as team_count
    FROM bids 
    WHERE session_id = @s_id AND round_num = 2
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