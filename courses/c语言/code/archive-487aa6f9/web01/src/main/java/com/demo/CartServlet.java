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
 * Servlet implementation class CartServlet
 */
@WebServlet("/CartServlet")
public class CartServlet extends HttpServlet {
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
    public CartServlet() {
        super();
        // TODO Auto-generated constructor stub
    }

	/**
	 * @see HttpServlet#doGet(HttpServletRequest request, HttpServletResponse response)
	 */
	protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		// TODO Auto-generated method stub
		HttpSession session = request.getSession();
		ArrayList <Product> products=null;
     	products =new ArrayList<Product>();
		User user = (User) session.getAttribute("user");
		Cart cart = user.getShoppingCart();
		 if (cart == null) {
	        cart = new Cart();
	    }else {
	    	products=cart.getProducts();
		    session.setAttribute("products", products); // 更新会话中的User对象
	    }
	    double total = cart.calculateTotalPrice();
	    session.setAttribute("cartTotal", total);
	    response.sendRedirect("cart.jsp");
	}

	/**
	 * @see HttpServlet#doPost(HttpServletRequest request, HttpServletResponse response)
	 */
	protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		// TODO Auto-generated method stub
		String action = request.getParameter("action");
        HttpSession session = request.getSession();
        User user = (User) session.getAttribute("user");
        Cart cart = user.getShoppingCart();
        if (cart == null) {
            cart = new Cart();
        }
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
    	 
        if ("add".equals(action)) {
            String productId = request.getParameter("productId");
            Product product = getProductById(productList,productId);
            cart.addProduct(product);
        } else if ("remove".equals(action)) {
            String productId = request.getParameter("productId");
            Product product = getProductById(productList,productId);
            if (product != null) {
            	cart.removeProduct(product);
            }
        }else {
        	cart.clear();
        }
        user.setShoppingCart(cart);
        session.setAttribute("user", user); // 更新会话中的User对象
        // 重定向到购物车页面
        // 更新购物车总价
        doGet(request, response);
    }
	
	private Product getProductById(ArrayList <Product> productList,String id) {
        // 根据ID查找产品
    	Product product=null;
   	 	for (Product p : productList) {
            if (p.getId().equals(id)) {
                product = p;
                break; // 找到后退出循环
            }
        }//查找商品方法
   	 	return product;
    }
}