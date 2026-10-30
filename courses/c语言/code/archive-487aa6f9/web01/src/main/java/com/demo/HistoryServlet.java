package com.demo;

import java.io.*;
import java.util.*;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.*;
import java.sql.*;
/**
 * Servlet implementation class HistoryServlet
 */
@WebServlet("/HistoryServlet")
public class HistoryServlet extends HttpServlet {
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
    public HistoryServlet() {
        super();
        // TODO Auto-generated constructor stub
    }

    private void updateBrowsingHistory(User user, Product product) {
        boolean found=false;
        for (BrowsingHistory existingHistory : user.getBrowsingHistories()) {
            if (existingHistory.getProduct().getId().equals(product.getId())) {
                existingHistory.incrementViewCount();
                found=true;
                break;
            }
        }
        if(!found) {
        	BrowsingHistory browsingHistory = new BrowsingHistory(product);
        	user.addBrowsingHistory(browsingHistory);
        }
    }
    
	protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		doPost(request, response);
	}

	/**
	 * @see HttpServlet#doPost(HttpServletRequest request, HttpServletResponse response)
	 */
	protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		// TODO Auto-generated method stub
		HttpSession session = request.getSession(true);
        User user = (User) session.getAttribute("user");
        if (user == null) {
            response.sendRedirect("login.jsp");
        } else {
            String productId = request.getParameter("productId");
    		ArrayList <Product> productList=null;
        	productList =new ArrayList<Product>();
        	// 数据库导入
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
        	Product product=null;
       	 for (Product p : productList) {
                if (p.getId().equals(productId)) {
                    product = p;
                    break; // 找到后退出循环
                }
            }//查找商品
       	 
            if (product != null) {
                updateBrowsingHistory(user, product);
                session.setAttribute("user", user); // 更新会话中的User对象
                request.setAttribute("product", product);
                request.getRequestDispatcher("/productDetail.jsp").forward(request, response);
            } else {
            	System.out.println("未找到商品");
            }
        }
	}
  
}

