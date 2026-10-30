package com.experiment6.database;

import com.experiment6.common.AppLogger;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.util.ArrayList;
import java.util.List;

/**
 * 用户画像 DAO。
 */
public class UserProfileDao {
    /**
     * 查询用户画像表。
     * @return List<String>
     */
    public List<String[]> fetchAll() {
        List<String[]> list = new ArrayList<>();
        String sql = "SELECT user_id, ip_address, visit_count, preferred_content_type, interest_tags FROM user_profile";
        try (Connection conn = DatabaseManager.getConnection();
             PreparedStatement ps = conn != null ? conn.prepareStatement(sql) : null;
             ResultSet rs = ps != null ? ps.executeQuery() : null) {
            if (rs == null) return list;
            while (rs.next()) {
                list.add(new String[]{
                        rs.getString("user_id"),
                        rs.getString("ip_address"),
                        String.valueOf(rs.getInt("visit_count")),
                        rs.getString("preferred_content_type"),
                        rs.getString("interest_tags")
                });
            }
        } catch (Exception e) {
            AppLogger.error("查询 user_profile 失败", e);
        }
        return list;
    }
}
