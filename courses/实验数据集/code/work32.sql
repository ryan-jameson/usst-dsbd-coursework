SELECT 
    AVG(CO) AS Avg_CO
FROM air_fangzhicheng
WHERE Date IN ('2013-01-02', '2013-01-04');

WITH avg_co AS (
    SELECT AVG(CO) AS AvgCO
    FROM air_fangzhicheng
    WHERE Date IN ('2013-01-02', '2013-01-04')
)
UPDATE air_fangzhicheng
SET CO = (SELECT AvgCO FROM avg_co)
WHERE Date = '2013-01-03';

SELECT *
FROM air_fangzhicheng
WHERE Date = '2013-01-03';