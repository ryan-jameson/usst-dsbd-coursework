SELECT 
    Date,
    PM25,
    PollutionRate
FROM air_stadium
WHERE PM25 > (
      SELECT AVG(PM25)
      FROM air_stadium
      WHERE PM25 IS NOT NULL
  );