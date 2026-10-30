package com.demo;

import java.io.*;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.*;

/**
 * Servlet implementation class LoginServlet
 */
@WebServlet("/LoginServlet")
public class LoginServlet extends HttpServlet {
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
    public LoginServlet() {
        super();
        // TODO Auto-generated constructor stub
    }

	/**
	 * @see HttpServlet#doGet(HttpServletRequest request, HttpServletResponse response)
	 */
	protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		// TODO Auto-generated method stub
		response.getWriter().append("Served at: ").append(request.getContextPath());
	}

	/**
	 * @see HttpServlet#doPost(HttpServletRequest request, HttpServletResponse response)
	 */
	protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		// TODO Auto-generated method stub
		String username = request.getParameter("username");
        String password = request.getParameter("password");
        if("admin".equals(username) && "admin".equals(password)) {
            
            // 登录成功，转发到管理员界面
          	response.sendRedirect("AdminServlet");
          }else {
        	  ArrayList <User> userList=null;
          	userList =new ArrayList<User>();
          	try {
          		PreparedStatement pstmt=connection.prepareStatement("select * from users");
          		ResultSet rs=pstmt.executeQuery();
          		while(rs.next()) {
          			User user=new User();
          			user.setUsername(rs.getString("username"));
          			user.setPassword(rs.getString("password"));
          			userList.add(user);
          		}//将数据库数据导入
          	}catch (SQLException e) {
          		System.out.println("数据库连接失败");
          		e.printStackTrace();
          	}
          	User user=new User(username,password);
              if (find(userList,user)) {
              	
              	// 设置请求属性表示用户已登录
                  request.setAttribute("isLoggedIn", true);
                  // 将用户对象存储到session中
                  HttpSession session = request.getSession();
                  session.setAttribute("user", user);
                  
                  // 设置cookie
                  Cookie cookie = new Cookie("userId", user.getUsername());
                  cookie.setMaxAge(60 * 60 * 24); // 1天
                  cookie.setPath("/");
                  cookie.setSecure(true);
                  response.addCookie(cookie);
               // 登录成功，重定向到主页或其他页面
                  response.sendRedirect("main.jsp");
              } else {
                  // 登录失败，返回登录页面并显示错误消息
                  request.setAttribute("errorMessage", "用户名或密码错误");
                  request.getRequestDispatcher("/login.jsp").forward(request, response);
              }
          }
        
	}
	private boolean find(ArrayList <User> userList,User user) {
		// 根据账号密码校验
   	 	for (User u : userList) {
            if (u.getUsername().equals(user.getUsername())) {
                if(u.getPassword().equals(user.getPassword())) {
                	return true;
                }
                break;
            }
        }//查找商品方法
   	 	return false;
	}
}
