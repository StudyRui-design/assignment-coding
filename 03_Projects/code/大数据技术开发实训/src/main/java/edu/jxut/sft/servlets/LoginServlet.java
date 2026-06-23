package edu.jxut.sft.servlets;

import edu.jxut.sft.untils.DbUtil;
import edu.jxut.sft.untils.PasswordUtil;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;
import java.io.IOException;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

// @WebServlet("/login")  // 已被 UserController 替代，禁用避免路由冲突
public class LoginServlet extends HttpServlet {

    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {
        req.setCharacterEncoding("UTF-8");

        String username = req.getParameter("username");
        String password = req.getParameter("password");

        // 参数空值校验
        if (username == null || username.trim().isEmpty()
                || password == null || password.trim().isEmpty()) {
            resp.setContentType("text/html;charset=UTF-8");
            resp.getWriter().write(
                "<script>alert('用户名和密码不能为空');window.location='login.html'</script>");
            return;
        }

        // 先查用户，再进行密码验证（不再明文对比密码）
        String sql = "SELECT password, real_name FROM user WHERE username = ?";
        try (Connection conn = DbUtil.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {

            ps.setString(1, username.trim());
            try (ResultSet rs = ps.executeQuery()) {
                if (rs.next()) {
                    String storedHash = rs.getString("password");
                    String realName = rs.getString("real_name");

                    // 使用 SHA-256 验证密码（兼容旧明文密码）
                    if (PasswordUtil.verify(password, storedHash)) {
                        // 登录成功，保存会话信息
                        HttpSession session = req.getSession();
                        session.setAttribute("username", username);
                        session.setAttribute("realName", realName);
                        resp.sendRedirect("index.html");
                    } else {
                        resp.setContentType("text/html;charset=UTF-8");
                        resp.getWriter().write(
                            "<script>alert('用户名或密码错误');window.location='login.html'</script>");
                    }
                } else {
                    resp.setContentType("text/html;charset=UTF-8");
                    resp.getWriter().write(
                        "<script>alert('用户名或密码错误');window.location='login.html'</script>");
                }
            }
        } catch (SQLException e) {
            e.printStackTrace();
            resp.setContentType("text/html;charset=UTF-8");
            resp.getWriter().write("<script>alert('系统错误，请稍后重试');window.location='login.html'</script>");
        }
    }
}