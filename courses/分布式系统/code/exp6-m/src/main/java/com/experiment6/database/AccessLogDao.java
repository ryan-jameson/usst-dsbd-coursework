package com.experiment6.database;

import com.experiment6.common.AppLogger;

import java.sql.Connection;
import java.sql.PreparedStatement;

/**
 * 访问日志 DAO。
 */
public class AccessLogDao {
    /**
     * 记录访问日志。
     */
    public void insert(String userId, String method, String path, String headers, int status, int responseTimeMs, boolean aiGenerated) {
        String sql = "INSERT INTO access_log (user_id, request_method, request_path, request_headers, response_status, response_time_ms, ai_generated) VALUES (?,?,?,?,?,?,?)";
        try (Connection conn = DatabaseManager.getConnection();
             PreparedStatement ps = conn != null ? conn.prepareStatement(sql) : null) {
            if (ps == null) return;
            ps.setString(1, userId);
            ps.setString(2, method);
            ps.setString(3, path);
            ps.setString(4, headers);
            ps.setInt(5, status);
            ps.setInt(6, responseTimeMs);
            ps.setBoolean(7, aiGenerated);
            ps.executeUpdate();
        } catch (Exception e) {
            AppLogger.error("写入 access_log 失败", e);
        }
    }
}
