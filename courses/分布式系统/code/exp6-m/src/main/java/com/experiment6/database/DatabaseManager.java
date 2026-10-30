package com.experiment6.database;

import com.experiment6.common.AppConfig;
import com.experiment6.common.AppLogger;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

/**
 * 数据库连接管理器。
 */
public class DatabaseManager {
    /**
     * 获取数据库连接。
     * @return Connection
     */
    public static Connection getConnection() {
        String host = AppConfig.get("DB_HOST", "localhost");
        String port = AppConfig.get("DB_PORT", "3306");
        String db = AppConfig.get("DB_NAME", "experiment6");
        String user = AppConfig.get("DB_USER", "root");
        String password = AppConfig.get("DB_PASSWORD", "");
        String url = "jdbc:mysql://" + host + ":" + port + "/" + db + "?useSSL=false&serverTimezone=UTC&characterEncoding=UTF-8";
        try {
            Class.forName("com.mysql.cj.jdbc.Driver");
            return DriverManager.getConnection(url, user, password);
        } catch (ClassNotFoundException | SQLException e) {
            AppLogger.error("数据库连接失败", e);
            return null;
        }
    }
}
