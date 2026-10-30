DELETE FROM air_caotan
WHERE Date BETWEEN '2013-01-01' AND '2013-01-04';

INSERT INTO air_caotan (DataID, SO2, NO2, PM10, CO, PM25, PollutionRate, Date)
SELECT 
    CONCAT('C', LPAD(ROW_NUMBER() OVER (ORDER BY Date), 4, '0')) AS DataID,  -- C0001, C0002...
    SO2,
    NO2,
    PM10,
    CO,
    PM25,
    PollutionRate,
    Date
FROM air_city_avg
WHERE Date BETWEEN '2013-01-01' AND '2013-01-04';

SELECT * FROM air_caotan
WHERE Date BETWEEN '2013-01-01' AND '2013-01-04';