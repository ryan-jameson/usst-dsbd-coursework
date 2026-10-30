Use auctiongamedb;
SET FOREIGN_KEY_CHECKS = 0;

TRUNCATE TABLE bids;
TRUNCATE TABLE items;
TRUNCATE TABLE players;
TRUNCATE TABLE teams;
TRUNCATE TABLE game_sessions;

SET FOREIGN_KEY_CHECKS = 1;

-- 验证是否清空
SELECT 'Tables Truncated' AS Status, COUNT(*) as Count FROM game_sessions;