USE 空气质量监测;
CREATE TABLE air_template (
                              DataID CHAR(5) NOT NULL PRIMARY KEY,   -- D0001 这样的主键
                              SO2 DECIMAL(6,2),
                              NO2 DECIMAL(6,2),
                              PM10 DECIMAL(6,2),
                              CO DECIMAL(6,2),
                              PM25 DECIMAL(6,2),
                              PollutionRate TINYINT,
                              Date DATE NOT NULL UNIQUE              -- 非空 + 非重复
);

-- ③ 用模板表复制出 5 个表（结构完全相同，只是表名不同）
CREATE TABLE air_caotan        LIKE air_template;  -- 草滩空气质量监测数据
CREATE TABLE air_fangzhicheng  LIKE air_template;  -- 纺织城空气质量监测数据
CREATE TABLE air_city_avg      LIKE air_template;  -- 全市平均空气监测质量数据
CREATE TABLE air_stadium       LIKE air_template;  -- 市人民体育场空气监测质量数据
CREATE TABLE air_changan       LIKE air_template;  -- 长安区空气质量监测数据

USE 空气质量监测;

TRUNCATE TABLE air_caotan;

SET @seq := 0;

SELECT @seq;

LOAD DATA LOCAL INFILE 'E:/Documents/caotan.csv'
    INTO TABLE air_caotan
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