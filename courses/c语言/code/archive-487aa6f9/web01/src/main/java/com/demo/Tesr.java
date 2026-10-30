package com.demo;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
 
public class Tesr {
    public static void main(String[] args) {
        // 数据库URL，用户名和密码
        String url = "jdbc:mysql://localhost:3306/web?serverTimezone=UTC";
        String user = "root";
        String password = "REDACTED_CONFIGURE_LOCALLY";
 
        try {
            // 加载并注册JDBC驱动
            Class.forName("com.mysql.cj.jdbc.Driver");
            // 建立数据库连接
            Connection connection = DriverManager.getConnection(url, user, password);
            System.out.println("数据库连接成功！");
            // 在这里可以执行SQL语句等操作
            // ...
            // 关闭连接
            connection.close();
        } catch (ClassNotFoundException e) {
            System.out.println("未找到JDBC驱动类");
            e.printStackTrace();
        } catch (SQLException e) {
            System.out.println("数据库连接失败");
            e.printStackTrace();
        }
    }
}
