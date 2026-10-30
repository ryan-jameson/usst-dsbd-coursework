package com.demo;

import java.io.IOException;
import java.util.ArrayList;
import java.sql.*;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.*;

/**
 * Servlet implementation class MessageServlet
 */
@WebServlet("/MessageServlet")
public class MessageServlet extends HttpServlet {
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
    public MessageServlet() {
        super();
        // TODO Auto-generated constructor stub
    }

	/**
	 * @see HttpServlet#doGet(HttpServletRequest request, HttpServletResponse response)
	 */
	protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		// TODO Auto-generated method stub
		HttpSession session = request.getSession(false);
        if (session == null || session.getAttribute("user") == null) {
            response.sendRedirect("login.jsp"); // 重定向到登录页面
            return;
        }

        ArrayList<Message> messages = new ArrayList<>();
        try {
            PreparedStatement pstmt = connection.prepareStatement("SELECT * FROM messages");
            ResultSet rs = pstmt.executeQuery();
            while (rs.next()) {
                Message message = new Message(rs.getString("username"), rs.getString("message"));
                messages.add(message);
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
        request.setAttribute("messages", messages);
        request.getRequestDispatcher("/message.jsp").forward(request, response);
	}

	/**
	 * @see HttpServlet#doPost(HttpServletRequest request, HttpServletResponse response)
	 */
	protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		HttpSession session = request.getSession();
		 String username = ((User) session.getAttribute("user")).getUsername();
		    String message = request.getParameter("message");
		if(message!=null) {
			try  {
		        PreparedStatement pstmt = connection.prepareStatement("INSERT INTO messages (username, message) VALUES (?, ?)");
		        pstmt.setString(1, username);
		        pstmt.setString(2, message);
		        pstmt.executeUpdate();
		    } catch (SQLException e) {
		        e.printStackTrace();
		        request.setAttribute("errorMessage", e.getMessage());
		    }

		    doGet(request, response);
		}else {
			response.sendRedirect("main.jsp");
		}
	    
	}

}
