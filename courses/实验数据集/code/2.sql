USE 空气质量监测;

TRUNCATE TABLE air_fangzhicheng;

SET @seq := 0;

SELECT @seq;

LOAD DATA LOCAL INFILE 'E:/Documents/fangzhi.csv'
    INTO TABLE air_fangzhicheng
    CHARACTER SET gbk
    FIELDS TERMINATED BY ','
    ENCLOSED BY '"'
    LINES TERMINATED BY '\r\n'
    IGNORE 1 LINES
    (@SO2, @NO2, @PM10, @CO, @PM25, @PollutionRate, @DateRaw)
    SET
        DataID = CONCAT('D', LPAD(@seq := @seq + 1, 4, '0')),

        SO2 = NULLIF(NULLIF(NULLIF(@SO2, ''), '故障'), 'NA'),
        NO2 = NULLIF(NULLIF(NULLIF(@NO2, ''), '故障'), 'NA'),
        PM10 = NULLIF(NULLIF(NULLIF(@PM10, ''), '故障'), 'NA'),
        CO = NULLIF(NULLIF(NULLIF(@CO, ''), '故障'), 'NA'),
        PM25 = NULLIF(NULLIF(NULLIF(@PM25, ''), '故障'), 'NA'),
        PollutionRate = NULLIF(NULLIF(NULLIF(@PollutionRate, ''), '故障'), 'NA'),
        Date = STR_TO_DATE(REPLACE(@DateRaw, '/', '-'), '%Y-%m-%d');