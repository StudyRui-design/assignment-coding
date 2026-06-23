package edu.jxut.sft.servlets;

import edu.jxut.sft.untils.DbUtil;
import edu.jxut.sft.untils.PasswordUtil;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

// @WebServlet("/register")  // 已被 UserController 替代，禁用避免路由冲突
public class RegisterServlet extends HttpServlet {

    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {
        req.setCharacterEncoding("UTF-8");

        String username = req.getParameter("username");
        String password = req.getParameter("password");
        String realName = req.getParameter("realName");

        // 参数空值校验
        if (username == null || username.trim().isEmpty()
                || password == null || password.trim().isEmpty()
                || realName == null || realName.trim().isEmpty()) {
            resp.setContentType("text/html;charset=UTF-8");
            resp.getWriter().write(
                "<script>alert('所有字段不能为空');window.location='register.html'</script>");
            return;
        }

        // 检查用户名是否已存在
        try (Connection conn = DbUtil.getConnection()) {
            String checkSql = "SELECT COUNT(*) FROM user WHERE username = ?";
            try (PreparedStatement checkPs = conn.prepareStatement(checkSql)) {
                checkPs.setString(1, username.trim());
                try (ResultSet rs = checkPs.executeQuery()) {
                    if (rs.next() && rs.getInt(1) > 0) {
                        resp.setContentType("text/html;charset=UTF-8");
                        resp.getWriter().write(
                            "<script>alert('用户名已存在');window.location='register.html'</script>");
                        return;
                    }
                }
            }

            // 对密码进行 SHA-256 加密存储
            String encryptedPassword = PasswordUtil.encrypt(password);

            String sql = "INSERT INTO user (username, password, real_name) VALUES (?, ?, ?)";
            try (PreparedStatement ps = conn.prepareStatement(sql)) {
                ps.setString(1, username.trim());
                ps.setString(2, encryptedPassword);
                ps.setString(3, realName.trim());

                int rows = ps.executeUpdate();
                if (rows > 0) {
                    resp.sendRedirect("login.html");
                } else {
                    resp.setContentType("text/html;charset=UTF-8");
                    resp.getWriter().write(
                        "<script>alert('注册失败，请重试');window.location='register.html'</script>");
                }
            }
        } catch (SQLException e) {
            e.printStackTrace();
            resp.setContentType("text/html;charset=UTF-8");
            resp.getWriter().write(
                "<script>alert('注册失败：" + e.getMessage() + "');window.location='register.html'</script>");
        }
    }
}