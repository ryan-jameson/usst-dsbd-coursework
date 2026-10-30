package com.demo;

import java.io.IOException;
import java.util.*;
import java.sql.*;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.*;

/**
 * Servlet implementation class AdminServlet
 */
@WebServlet("/AdminServlet")
public class AdminServlet extends HttpServlet {
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
    public AdminServlet() {
        super();
        // TODO Auto-generated constructor stub
    }

	/**
	 * @see HttpServlet#doGet(HttpServletRequest request, HttpServletResponse response)
	 */
	protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		// TODO Auto-generated method stub
		HttpSession session = request.getSession(true);
		ArrayList <User> userList=null;
    	userList =new ArrayList<User>();
    	 ArrayList <Product> productList=null;
     	productList =new ArrayList<Product>();
     	try {
    		PreparedStatement pstmt=connection.prepareStatement("select * from product");
    		ResultSet rs=pstmt.executeQuery();
    		while(rs.next()) {
    			Product product=new Product();
    			product.setId(String.valueOf(rs.getInt("id")));
    			product.setImageUrl(rs.getString("imageUrl"));
    			product.setName(rs.getString("name"));
    			product.setDescription(rs.getString("description"));
    			product.setPrice(rs.getDouble("price"));
    			productList.add(product);
    		}//将数据库数据导入
    	}catch (SQLException e) {
    		System.out.println("数据库连接失败");
    		e.printStackTrace();
    	}
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
        session.setAttribute("userList", userList);
        session.setAttribute("productList", productList);

        response.sendRedirect("admin.jsp");
	}

	/**
	 * @see HttpServlet#doPost(HttpServletRequest request, HttpServletResponse response)
	 */
	protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		// TODO Auto-generated method stub
		 String action = request.getParameter("action");
		 
		 
		 String username = Optional.ofNullable(request.getParameter("username")).orElse("");
		    String password = Optional.ofNullable(request.getParameter("password")).orElse("");
		    String productId = Optional.ofNullable(request.getParameter("productid")).orElse("");
		    String productName = Optional.ofNullable(request.getParameter("productName")).orElse("");
		    String imageUrl = Optional.ofNullable(request.getParameter("imageUrl")).orElse("");
		    String productDescription = Optional.ofNullable(request.getParameter("productDescription")).orElse("");
		    String priceString = Optional.ofNullable(request.getParameter("productPrice")).orElse("0.00");
		    double productPrice = Double.parseDouble(priceString);

		    if ("addu".equals(action)) { // 添加用户
		        try {
		            PreparedStatement pstmt = connection.prepareStatement("INSERT INTO users (username, password) VALUES (?, ?)");
		            pstmt.setString(1, username);
		            pstmt.setString(2, password);
		            pstmt.executeUpdate();
		        } catch (SQLException e) {
		            e.printStackTrace();
		        }
		    } else if ("removeu".equals(action)) { // 删除用户或商品
		        if (username != null) {
		            try {
		                PreparedStatement pstmt = connection.prepareStatement("DELETE FROM users WHERE username = ?");
		                pstmt.setString(1, username);
		                pstmt.executeUpdate();
		            } catch (SQLException e) {
		                e.printStackTrace();
		            }
		        } else if ("removep".equals(action)) {
		            try {
		                PreparedStatement pstmt = connection.prepareStatement("DELETE FROM product WHERE id = ?");
		                pstmt.setString(1, productId);
		                pstmt.executeUpdate();
		            } catch (SQLException e) {
		                e.printStackTrace();
		            }
		        }
		    } else if ("addp".equals(action)) { // 添加商品
		        try {
		            PreparedStatement pstmt = connection.prepareStatement("INSERT INTO product (name, description, price, imageUrl) VALUES (?, ?, ?, ?)");
		            pstmt.setString(1, productName);
		            pstmt.setString(2, productDescription);
		            pstmt.setDouble(3, productPrice);
		            pstmt.setString(4, imageUrl); // 这里需要设置正确的图片路径
		            pstmt.executeUpdate();
		        } catch (SQLException e) {
		            e.printStackTrace();
		        }
		    }

		 // 重新加载用户列表
		    doGet(request, response);
	}

}
