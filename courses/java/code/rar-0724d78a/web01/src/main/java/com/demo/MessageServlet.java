package com.demo;

import java.io.IOException;
import java.util.*;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.*;

/**
 * Servlet implementation class MessageServlet
 */
@WebServlet("/MessageServlet")
public class MessageServlet extends HttpServlet {
	private static final long serialVersionUID = 1L;
    
    public MessageServlet() {
        super();
        // TODO Auto-generated constructor stub
    }

	/**
	 * @see HttpServlet#doGet(HttpServletRequest request, HttpServletResponse response)
	 */
	protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		// TODO Auto-generated method stub
		HttpSession session = request.getSession();
		
        if (session == null || session.getAttribute("user") == null) {
            response.sendRedirect("login.jsp"); // 重定向到登录页面
            return;
        }
        if (session.getAttribute("messages") == null) {
            session.setAttribute("messages", new ArrayList<Message>());
        }
        @SuppressWarnings("unchecked")
        List<Message> messages = (List<Message>) session.getAttribute("messages");
        session.setAttribute("messages", messages);
        request.getRequestDispatcher("/message.jsp").forward(request, response);
	}

	/**
	 * @see HttpServlet#doPost(HttpServletRequest request, HttpServletResponse response)
	 */
	protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		HttpSession session = request.getSession();
		 String username = ((User) session.getAttribute("user")).getUsername();
		    String message = request.getParameter("message");//用户名、留言信息
		if(message!=null) {
			if (session.getAttribute("messages") == null) {
	            session.setAttribute("messages", new ArrayList<Message>());
	        }
			@SuppressWarnings("unchecked")
			List<Message> messages = (List<Message>) session.getAttribute("messages");
	        Message newMessage = new Message(username, message, System.currentTimeMillis());
	        messages.add(newMessage);
			session.setAttribute("messages", messages);
		    doGet(request, response);
		}else {
			response.sendRedirect("main.jsp");
		}
	    
	}

}
