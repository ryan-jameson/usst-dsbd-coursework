-- ==========================================
-- 1. 初始化游戏环境
-- ==========================================
INSERT INTO game_sessions (status) VALUES ('WAITING');
SET @s_id = LAST_INSERT_ID(); -- 获取当前游戏ID

-- 创建6个组 (T1-T6)
INSERT INTO teams (session_id, team_name, balance) VALUES 
(@s_id, 'Team_A', 100), (@s_id, 'Team_B', 100), (@s_id, 'Team_C', 100),
(@s_id, 'Team_D', 100), (@s_id, 'Team_E', 100), (@s_id, 'Team_F', 100);

-- 获取队伍ID以便后续使用
SELECT team_id INTO @t1 FROM teams WHERE team_name='Team_A' AND session_id=@s_id;
SELECT team_id INTO @t2 FROM teams WHERE team_name='Team_B' AND session_id=@s_id;
SELECT team_id INTO @t3 FROM teams WHERE team_name='Team_C' AND session_id=@s_id;
SELECT team_id INTO @t4 FROM teams WHERE team_name='Team_D' AND session_id=@s_id;
SELECT team_id INTO @t5 FROM teams WHERE team_name='Team_E' AND session_id=@s_id;
SELECT team_id INTO @t6 FROM teams WHERE team_name='Team_F' AND session_id=@s_id;

-- 创建18名玩家 (每组3人)
-- 特殊设定：T1的第3人是T2的间谍，T2的第3人是T1的间谍
INSERT INTO players (team_id, true_team_id, player_name, is_spy) VALUES
(@t1, @t1, 'A_User1', 0), (@t1, @t1, 'A_User2', 0), (@t1, @t2, 'A_Spy_from_B', 1),
(@t2, @t2, 'B_User1', 0), (@t2, @t2, 'B_User2', 0), (@t2, @t1, 'B_Spy_from_A', 1),
(@t3, @t3, 'C_User1', 0), (@t3, @t3, 'C_User2', 0), (@t3, @t4, 'C_Spy_from_D', 1),
(@t4, @t4, 'D_User1', 0), (@t4, @t4, 'D_User2', 0), (@t4, @t3, 'D_Spy_from_C', 1),
(@t5, @t5, 'E_User1', 0), (@t5, @t5, 'E_User2', 0), (@t5, @t6, 'E_Spy_from_F', 1),
(@t6, @t6, 'F_User1', 0), (@t6, @t6, 'F_User2', 0), (@t6, @t5, 'F_Spy_from_E', 1);

-- 初始化藏品 (8件，A-H)
INSERT INTO items (session_id, item_code, item_name, base_price, current_value, increment_coeff) VALUES
(@s_id, 'A', '青铜爵', 70, 100, 20),
(@s_id, 'B', '玉如意', 70, 110, 10),
(@s_id, 'C', '唐三彩', 50, 80, 30),
(@s_id, 'D', '金缕衣', 40, 40, 20),
(@s_id, 'E', '青花瓷', 40, 80, 10), 
(@s_id, 'F', '兵马俑', 30, 40, 15),
(@s_id, 'G', '宣德炉', 20, 20, 30),
(@s_id, 'H', '清明图', 10, 50, 5);