package com.demo;

import java.io.IOException;
import java.sql.*;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

/**
 * Servlet implementation class RegisterServlet
 */
@WebServlet("/RegisterServlet")
public class RegisterServlet extends HttpServlet {
	private static final long serialVersionUID = 1L;
	 Connection connection=null;
	    public void init() {
	    	String url = "jdbc:mysql://localhost:3306/web?serverTimezone=UTC";
	    	String usern = "root";
	    	String password = "REDACTED_CONFIGURE_LOCALLY";

	    	try {
	        // 加载并注册JDBC驱动
	    		Class.forName("com.mysql.cj.jdbc.Driver");
	        // 建立数据库连接
	    		connection = DriverManager.getConnection(url, usern, password);
	    	} catch (ClassNotFoundException e) {
	    		System.out.println("未找到JDBC驱动类");
	    		e.printStackTrace();
	    	} catch (SQLException e) {
	    		System.out.println("数据库连接失败");
	    		e.printStackTrace();
	    	}
	    }
    public RegisterServlet() {
        super();
        // TODO Auto-generated constructor stub
    }

	/**
	 * @see HttpServlet#doGet(HttpServletRequest request, HttpServletResponse response)
	 */
	protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		try {
			String username = request.getParameter("username");
	        String password = request.getParameter("password");
            String sql = "INSERT INTO users (username, password) VALUES (?, ?)";//连接数据库
            PreparedStatement statement = connection.prepareStatement(sql);
            statement.setString(1, username);
            statement.setString(2, password);
            statement.executeUpdate();
            response.sendRedirect("login.jsp"); // 注册成功后重定向登录页面
        } catch (Exception e) {
            e.printStackTrace();
            System.out.println("登录错误，或数据库连接失败");
        }
    }

	/**
	 * @see HttpServlet#doPost(HttpServletRequest request, HttpServletResponse response)
	 */
	protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		// TODO Auto-generated method stub
		doGet(request, response);
	}

}
