-- ==========================================
-- 1. 第三轮 环境准备
-- ==========================================
-- 确保变量延续 (防止断连)
SELECT session_id INTO @s_id FROM game_sessions ORDER BY session_id DESC LIMIT 1;
-- 队伍 ID
SELECT team_id INTO @t1 FROM teams WHERE team_name='Team_A' AND session_id=@s_id; -- A组
SELECT team_id INTO @t4 FROM teams WHERE team_name='Team_D' AND session_id=@s_id; -- D组
SELECT team_id INTO @t6 FROM teams WHERE team_name='Team_F' AND session_id=@s_id; -- F组
-- 藏品 ID
SELECT item_id INTO @iE FROM items WHERE item_code='E' AND session_id=@s_id;
SELECT item_id INTO @iG FROM items WHERE item_code='G' AND session_id=@s_id;

-- 标记进入第三轮
UPDATE game_sessions SET status='ROUND_3' WHERE session_id=@s_id;

-- ==========================================
-- 2. 第三轮 出价阶段 (混乱的开始)
-- ==========================================

-- [场景 A：A组的内忧]
-- A组本体策略：剩余20元，必须拿下 G (起拍20)。
-- 派出 B_spy_from_A ,卧底选择不动


-- B组间谍 (A_Spy_from_B) 也上场了！
-- 他以 A组的名义对 G 出价 20。
INSERT INTO bids (session_id, round_num, phase_type, item_id, team_id, player_id, bid_amount) 
SELECT @s_id, 3, 'INITIAL', @iG, @t1, player_id, 20 
FROM players WHERE team_id=@t1 AND is_spy=1 LIMIT 1;


-- [场景 D：D组的搅局]
-- D组派出卧底 (D_Spy_from_C)，同时对 E 和 G 出价搅局。
-- 第三轮允许每组对 2 种藏品出价。
-- D组余额 60，E起拍40，G起拍20，刚好 60，资金链极限操作。
INSERT INTO bids (session_id, round_num, phase_type, item_id, team_id, player_id, bid_amount) VALUES
(@s_id, 3, 'INITIAL', @iE, @t4, (SELECT player_id FROM players WHERE team_id=@t4 AND is_spy=1 LIMIT 1), 40),
(@s_id, 3, 'INITIAL', @iG, @t4, (SELECT player_id FROM players WHERE team_id=@t4 AND is_spy=1 LIMIT 1), 20);


-- [场景 F：F组的进击]
-- F组派出 F_User2 (User1 R1已用, Spy R2已用)。
-- F组余额 100，土豪进场，同时对 E(40) 和 G(20) 出价。
INSERT INTO bids (session_id, round_num, phase_type, item_id, team_id, player_id, bid_amount) VALUES
(@s_id, 3, 'INITIAL', @iE, @t6, (SELECT player_id FROM players WHERE team_id=@t6 AND player_name='F_User2' LIMIT 1), 50),
(@s_id, 3, 'INITIAL', @iG, @t6, (SELECT player_id FROM players WHERE team_id=@t6 AND player_name='F_User2' LIMIT 1), 25);


-- ==========================================
-- 3. 第三轮 结算 (Settlement)
-- ==========================================

-- [分析 G 的局势]
-- 出价方：Team_A , Team_D, Team_F。
-- 涉及队伍数：3 个组。
-- 判定：触发多人冲突 (Conflict)，流拍，价值上升。
UPDATE items SET status = 'AVAILABLE' WHERE item_id = @iG;

-- [分析 E 的局势]
-- 出价方：Team_D (卧底), Team_F (普通人)。
-- 涉及队伍数：2 个组。
-- 判定：触发对决 (DUEL)。
-- 虽然 D 是卧底乱搞，但规则上只要有2组出价就进入对决。

-- [E 的对决阶段]
-- F组势在必得，追加报价到 60。
INSERT INTO bids (session_id, round_num, phase_type, item_id, team_id, player_id, bid_amount) 
SELECT @s_id, 3, 'DUEL', @iE, @t6, player_id, 60 
FROM players WHERE team_id=@t6 AND player_name='F_User2' LIMIT 1; 
-- 注意：规则说“由从两组各自指定任意一名成员非公开出价”，这里假设 F 组还是让懂行情的 User2 继续。

-- D组 (卧底操作)：既然是搅浑水，他可能选择“放弃加价”或者“乱加价导致D组破产”。
-- 假设 D组卧底现在的目的是保住 D 的钱不动（因为他是 C 的卧底，C 没钱了，他不想让 D 拿到 E 变强，也不想 D 花钱）。
-- 或者他故意出个低价 40 (放弃)。
INSERT INTO bids (session_id, round_num, phase_type, item_id, team_id, player_id, bid_amount) 
SELECT @s_id, 3, 'DUEL', @iE, @t4, player_id, 40 
FROM players WHERE team_id=@t4 AND is_spy=1 LIMIT 1;

-- 结果：F组以 60 拿下 E。
UPDATE teams SET balance = balance - 60 WHERE team_id = @t6;
UPDATE items SET owner_team_id = @t6, status = 'SOLD' WHERE item_id = @iE;


-- ==========================================
-- 4. 第三轮 价值核算 (Value Calculation)
-- ==========================================
-- 规则：当前价值 = 累加 (本轮参与队伍数 * 系数)

-- G (系数30): 参与组 A, D, F (3个组) -> 价值 + 90
-- E (系数10): 参与组 D, F (2个组) -> 价值 + 20

UPDATE items i
JOIN (
    SELECT item_id, COUNT(DISTINCT team_id) as team_count
    FROM bids 
    WHERE session_id = @s_id AND round_num = 3
    GROUP BY item_id
) b ON i.item_id = b.item_id
SET i.current_value = i.current_value + (b.team_count * i.increment_coeff);


-- ==========================================
-- 5. 战局盘点
-- ==========================================
-- 此时：
-- A组：余额20，无收获 (G流拍)。
-- B组：余额100，无收获。
-- C组：余额5，拥有 F。
-- D组：余额60，拥有 D (卧底搅黄了 E 的购买，或者说没抢过 F)。
-- E组：余额10，拥有 B。
-- F组：余额40 (100-60)，拥有 E。
-- G 依然在场上，价值暴涨。

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