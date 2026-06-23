package edu.jxut.sft.servlets;  // 添加这句包声明
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
import edu.jxut.sft.untils.DbUtil;// 添加这行导入DBUtil

import javax.servlet.ServletException;

@WebServlet("/login") // 对应登录表单的action
public class LoginServlet extends HttpServlet {
    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        // 获取表单数据
        String username = req.getParameter("username");
        String password = req.getParameter("password");

        // 数据库验证
        try (Connection conn = DbUtil.getConnection()) {
            // 打印连接，确认是否成功获取
            System.out.println("数据库连接：" + conn);

            String sql = "SELECT * FROM user WHERE username = ? AND password = ?";
            PreparedStatement ps = conn.prepareStatement(sql);
            ps.setString(1, username);
            ps.setString(2, password);
            ResultSet rs = ps.executeQuery();

            if (rs.next()) {
                // 登录成功，跳转到首页（index.html）
                resp.sendRedirect("index.html");
            } else {
                // 登录失败，返回登录页并提示
                resp.setContentType("text/html;charset=UTF-8");
                resp.getWriter().write("<script>alert('用户名或密码错误');window.location='login.html'</script>");
            }
        } catch (SQLException e) {
            e.printStackTrace();
            resp.getWriter().write("登录失败，数据库错误");
        }
    }
}