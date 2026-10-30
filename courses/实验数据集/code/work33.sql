CREATE VIEW grassland_vs_city AS
SELECT 
	g.DataID,
    g.Date,
    g.PM25 AS Grassland_PM25,
    c.PM25 AS City_Avg_PM25
FROM air_caotan g ,air_city_avg c
where g.Date=c.Date
WITH CHECK OPTION;

SELECT * FROM 空气质量监测.grassland_vs_city;

SELECT COUNT(*) AS formerDays
FROM air_caotan g
WHERE PM25=(
      SELECT PM25
      FROM air_city_avg c
      WHERE g.Date=c.date
  );-- 更改前

UPDATE grassland_vs_city
SET City_Avg_PM25 = Grassland_PM25
WHERE City_Avg_PM25 > Grassland_PM25;

SELECT COUNT(*) AS alterDays
FROM air_caotan g
WHERE PM25=(
      SELECT PM25
      FROM air_city_avg c
      WHERE g.Date=c.date
  );-- 更改后,查看有哪些不同

CREATE VIEW grassland_pollution_count AS
SELECT 
    PollutionRate,
    COUNT(*) AS DaysCount
FROM air_caotan
WHERE PollutionRate IS NOT NULL
GROUP BY PollutionRate
ORDER BY PollutionRate;

SELECT * FROM 空气质量监测.grassland_pollution_count;