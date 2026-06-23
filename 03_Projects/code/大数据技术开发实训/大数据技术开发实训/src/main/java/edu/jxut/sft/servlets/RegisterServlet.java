package edu.jxut.sft.servlets;  // 包声明（确保与文件目录一致）
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import edu.jxut.sft.untils.DbUtil;

@WebServlet("/register")
public class RegisterServlet extends HttpServlet {
    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        // 1. 先处理请求参数的中文乱码（关键！避免前端传中文时打印乱码）
        req.setCharacterEncoding("UTF-8");

        // 2. 获取注册信息
        String username = req.getParameter("username");
        String password = req.getParameter("password");
        String realName = req.getParameter("realName");

        // 3. 打印获取到的参数（核心：验证数据是否传递成功）
        System.out.println("=== 前端传递的注册参数 ===");
        System.out.println("用户名（username）：" + username);
        System.out.println("密码（password）：" + password);
        System.out.println("真实姓名（realName）：" + realName);
        System.out.println("==========================");

        // 4. 插入数据库（原有逻辑不变）
        try (Connection conn = DbUtil.getConnection()) {
            System.out.println("数据库连接：" + conn);
            // 注意：SQL中的字段名要和数据库表一致！
            // 若之前创建的user表中没有real_name字段，需先在数据库添加该字段（后面会补充说明）
            String sql = "INSERT INTO user (username, password, real_name) VALUES (?, ?, ?)";
            System.out.println("数据库连接：" + sql);
            PreparedStatement ps = conn.prepareStatement(sql);
            ps.setString(1, username);
            ps.setString(2, password); // 实际项目需加密（如MD5）
            ps.setString(3, realName);

            int rows = ps.executeUpdate();
            if (rows > 0) {
                // 注册成功，跳转到登录页
                resp.sendRedirect("login.html");
            } else {
                resp.setContentType("text/html;charset=UTF-8");
                resp.getWriter().write("<script>alert('注册失败，请重试');window.location='register.html'</script>");
            }
        } catch (SQLException e) {
            // 打印异常信息（方便排查数据库相关问题）
            e.printStackTrace();
            resp.setContentType("text/html;charset=UTF-8");
            // 用户名重复或字段不存在等异常，都能通过alert提示
            resp.getWriter().write("<script>alert('注册失败：" + e.getMessage() + "');window.location='register.html'</script>");
        }
    }
}