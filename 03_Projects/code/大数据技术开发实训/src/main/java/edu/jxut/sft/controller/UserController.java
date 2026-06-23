package edu.jxut.sft.controller;

import edu.jxut.sft.untils.DbUtil;
import edu.jxut.sft.untils.PasswordUtil;
import org.springframework.web.bind.annotation.*;

import javax.servlet.http.HttpSession;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;

/**
 * 用户登录/注册 Controller
 */
@RestController
public class UserController {

    /**
     * 用户登录
     */
    @PostMapping("/login")
    public String login(@RequestParam String username,
                        @RequestParam String password,
                        HttpSession session) {
        if (username == null || username.trim().isEmpty()
                || password == null || password.trim().isEmpty()) {
            return "<script>alert('用户名和密码不能为空');window.location='login.html'</script>";
        }

        String sql = "SELECT password, real_name FROM user WHERE username = ?";
        try (Connection conn = DbUtil.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {

            ps.setString(1, username.trim());
            try (ResultSet rs = ps.executeQuery()) {
                if (rs.next()) {
                    String storedHash = rs.getString("password");
                    String realName = rs.getString("real_name");

                    if (PasswordUtil.verify(password, storedHash)) {
                        session.setAttribute("username", username.trim());
                        session.setAttribute("realName", realName);
                        return "<script>window.location='index.html'</script>";
                    }
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
            return "<script>alert('系统错误，请稍后重试');window.location='login.html'</script>";
        }

        return "<script>alert('用户名或密码错误');window.location='login.html'</script>";
    }

    /**
     * 用户注册
     */
    @PostMapping("/register")
    public String register(@RequestParam String username,
                           @RequestParam String password,
                           @RequestParam String realName) {
        if (username == null || username.trim().isEmpty()
                || password == null || password.trim().isEmpty()
                || realName == null || realName.trim().isEmpty()) {
            return "<script>alert('所有字段不能为空');window.location='register.html'</script>";
        }

        try (Connection conn = DbUtil.getConnection()) {
            // 检查用户名是否已存在
            String checkSql = "SELECT COUNT(*) FROM user WHERE username = ?";
            try (PreparedStatement checkPs = conn.prepareStatement(checkSql)) {
                checkPs.setString(1, username.trim());
                try (ResultSet rs = checkPs.executeQuery()) {
                    if (rs.next() && rs.getInt(1) > 0) {
                        return "<script>alert('用户名已存在');window.location='register.html'</script>";
                    }
                }
            }

            // 加密密码
            String encryptedPassword = PasswordUtil.encrypt(password);

            String sql = "INSERT INTO user (username, password, real_name) VALUES (?, ?, ?)";
            try (PreparedStatement ps = conn.prepareStatement(sql)) {
                ps.setString(1, username.trim());
                ps.setString(2, encryptedPassword);
                ps.setString(3, realName.trim());

                int rows = ps.executeUpdate();
                if (rows > 0) {
                    return "<script>alert('注册成功，请登录');window.location='login.html'</script>";
                } else {
                    return "<script>alert('注册失败，请重试');window.location='register.html'</script>";
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
            return "<script>alert('注册失败，请稍后重试');window.location='register.html'</script>";
        }
    }

    /**
     * 退出登录
     */
    @GetMapping("/logout")
    public String logout(HttpSession session) {
        session.invalidate();
        return "<script>window.location='login.html'</script>";
    }

    /**
     * 获取用户列表
     */
    @GetMapping("/user/list")
    public String userList() {
        StringBuilder sb = new StringBuilder();
        sb.append("[");
        String sql = "SELECT id, username, real_name, gender, birthday, phone, address, user_type FROM user ORDER BY id";
        try (Connection conn = DbUtil.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql);
             ResultSet rs = ps.executeQuery()) {
            boolean first = true;
            while (rs.next()) {
                if (!first) sb.append(",");
                first = false;
                sb.append("{");
                sb.append("\"id\":").append(rs.getInt("id")).append(",");
                sb.append("\"username\":\"").append(escapeJson(rs.getString("username"))).append("\",");
                sb.append("\"realName\":\"").append(escapeJson(rs.getString("real_name"))).append("\",");
                sb.append("\"gender\":\"").append(escapeJson(rs.getString("gender"))).append("\",");
                String birthday = rs.getString("birthday");
                sb.append("\"birthday\":\"").append(birthday != null ? birthday : "").append("\",");
                sb.append("\"phone\":\"").append(escapeJson(rs.getString("phone"))).append("\",");
                sb.append("\"address\":\"").append(escapeJson(rs.getString("address"))).append("\",");
                sb.append("\"userType\":\"").append(escapeJson(rs.getString("user_type"))).append("\"");
                sb.append("}");
            }
        } catch (Exception e) {
            e.printStackTrace();
            return "[]";
        }
        sb.append("]");
        return sb.toString();
    }

    /**
     * 添加用户
     */
    @PostMapping("/user/add")
    public String userAdd(@RequestParam String username,
                          @RequestParam String password,
                          @RequestParam String realName,
                          @RequestParam(required = false) String gender,
                          @RequestParam(required = false) String birthday,
                          @RequestParam(required = false) String phone,
                          @RequestParam(required = false) String address,
                          @RequestParam(required = false) String userType) {
        if (username == null || username.trim().isEmpty()
                || password == null || password.trim().isEmpty()
                || realName == null || realName.trim().isEmpty()) {
            return "<script>alert('用户名、密码、真实姓名不能为空');history.back()</script>";
        }

        try (Connection conn = DbUtil.getConnection()) {
            // 检查用户名是否已存在
            String checkSql = "SELECT COUNT(*) FROM user WHERE username = ?";
            try (PreparedStatement checkPs = conn.prepareStatement(checkSql)) {
                checkPs.setString(1, username.trim());
                try (ResultSet rs = checkPs.executeQuery()) {
                    if (rs.next() && rs.getInt(1) > 0) {
                        return "<script>alert('用户名已存在');history.back()</script>";
                    }
                }
            }

            String encryptedPassword = PasswordUtil.encrypt(password);
            String sql = "INSERT INTO user (username, password, real_name, gender, birthday, phone, address, user_type) " +
                         "VALUES (?, ?, ?, ?, ?, ?, ?, ?)";
            try (PreparedStatement ps = conn.prepareStatement(sql)) {
                ps.setString(1, username.trim());
                ps.setString(2, encryptedPassword);
                ps.setString(3, realName.trim());
                ps.setString(4, (gender != null && !gender.isEmpty()) ? gender : null);
                // 生日字段：只有非空且格式正确才设置，否则设为 NULL
                String bd = (birthday != null && !birthday.isEmpty()) ? birthday.trim() : null;
                if (bd != null) {
                    try { java.sql.Date.valueOf(bd); } catch (Exception ex) { bd = null; }
                }
                ps.setString(5, bd);
                ps.setString(6, (phone != null && !phone.isEmpty()) ? phone : null);
                ps.setString(7, (address != null && !address.isEmpty()) ? address : null);
                ps.setString(8, (userType != null && !userType.isEmpty()) ? userType : "学员");

                int rows = ps.executeUpdate();
                if (rows > 0) {
                    return "<script>alert('添加用户成功');window.location='userList.html'</script>";
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
            return "<script>alert('添加失败，请稍后重试');history.back()</script>";
        }
        return "<script>alert('添加失败');history.back()</script>";
    }

    /**
     * 更新用户
     */
    @PostMapping("/user/update")
    public String userUpdate(@RequestParam Integer id,
                             @RequestParam String realName,
                             @RequestParam(required = false) String gender,
                             @RequestParam(required = false) String birthday,
                             @RequestParam(required = false) String phone,
                             @RequestParam(required = false) String address,
                             @RequestParam(required = false) String userType) {
        if (id == null) {
            return "<script>alert('用户ID不能为空');history.back()</script>";
        }

        String sql = "UPDATE user SET real_name=?, gender=?, birthday=?, phone=?, address=?, user_type=? WHERE id=?";
        try (Connection conn = DbUtil.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setString(1, (realName != null && !realName.isEmpty()) ? realName.trim() : null);
            ps.setString(2, (gender != null && !gender.isEmpty()) ? gender : null);
            // 生日字段：只有非空且格式正确才设置，否则设为 NULL
            String bd = (birthday != null && !birthday.isEmpty()) ? birthday.trim() : null;
            if (bd != null) {
                try { java.sql.Date.valueOf(bd); } catch (Exception ex) { bd = null; }
            }
            ps.setString(3, bd);
            ps.setString(4, (phone != null && !phone.isEmpty()) ? phone : null);
            ps.setString(5, (address != null && !address.isEmpty()) ? address : null);
            ps.setString(6, (userType != null && !userType.isEmpty()) ? userType : "学员");
            ps.setInt(7, id);

            int rows = ps.executeUpdate();
            if (rows > 0) {
                return "<script>alert('修改用户成功');window.location='userList.html'</script>";
            } else {
                return "<script>alert('未找到该用户');history.back()</script>";
            }
        } catch (Exception e) {
            e.printStackTrace();
            return "<script>alert('修改失败，请稍后重试');history.back()</script>";
        }
    }

    /**
     * 删除用户
     */
    @PostMapping("/user/delete")
    public String userDelete(@RequestParam Integer id) {
        if (id == null) {
            return "<script>alert('用户ID不能为空');history.back()</script>";
        }

        // 不允许删除 admin 用户
        String checkSql = "SELECT username FROM user WHERE id = ?";
        try (Connection conn = DbUtil.getConnection();
             PreparedStatement ps = conn.prepareStatement(checkSql)) {
            ps.setInt(1, id);
            try (ResultSet rs = ps.executeQuery()) {
                if (rs.next() && "admin".equals(rs.getString("username"))) {
                    return "<script>alert('不能删除超级管理员账号');history.back()</script>";
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        }

        String sql = "DELETE FROM user WHERE id = ?";
        try (Connection conn = DbUtil.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setInt(1, id);
            int rows = ps.executeUpdate();
            if (rows > 0) {
                return "<script>alert('删除用户成功');window.location='userList.html'</script>";
            } else {
                return "<script>alert('未找到该用户');history.back()</script>";
            }
        } catch (Exception e) {
            e.printStackTrace();
            return "<script>alert('删除失败，请稍后重试');history.back()</script>";
        }
    }

    /**
     * 根据ID获取单个用户信息（用于修改页面回显）
     */
    @GetMapping("/user/get")
    public String userGet(@RequestParam Integer id) {
        String sql = "SELECT id, username, real_name, gender, birthday, phone, address, user_type FROM user WHERE id = ?";
        try (Connection conn = DbUtil.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setInt(1, id);
            try (ResultSet rs = ps.executeQuery()) {
                if (rs.next()) {
                    StringBuilder sb = new StringBuilder();
                    sb.append("{");
                    sb.append("\"id\":").append(rs.getInt("id")).append(",");
                    sb.append("\"username\":\"").append(escapeJson(rs.getString("username"))).append("\",");
                    sb.append("\"realName\":\"").append(escapeJson(rs.getString("real_name"))).append("\",");
                    sb.append("\"gender\":\"").append(escapeJson(rs.getString("gender"))).append("\",");
                    String birthday = rs.getString("birthday");
                    sb.append("\"birthday\":\"").append(birthday != null ? birthday : "").append("\",");
                    sb.append("\"phone\":\"").append(escapeJson(rs.getString("phone"))).append("\",");
                    sb.append("\"address\":\"").append(escapeJson(rs.getString("address"))).append("\",");
                    sb.append("\"userType\":\"").append(escapeJson(rs.getString("user_type"))).append("\"");
                    sb.append("}");
                    return sb.toString();
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return "{}";
    }

    private String escapeJson(String s) {
        if (s == null) return "";
        return s.replace("\\", "\\\\")
                .replace("\"", "\\\"")
                .replace("\n", "\\n")
                .replace("\r", "\\r")
                .replace("\t", "\\t");
    }
}
