-- 先找出全市平均 CO 小于 50 的日期
WITH c50d AS (
    SELECT Date, CO, PollutionRate
    FROM air_city_avg
    WHERE CO < 50
    GROUP BY Date
),
-- 再找市体育场当天无 CO 数据的日期
no_co AS (
    SELECT Date
    FROM air_stadium
    WHERE CO IS NULL
)
-- 最终连接两者
SELECT 
    c50d.Date,
    c50d.CO ,
    c50d.Pollutionrate
FROM c50d
INNER JOIN no_co ON c50d.Date = no_co.Date;