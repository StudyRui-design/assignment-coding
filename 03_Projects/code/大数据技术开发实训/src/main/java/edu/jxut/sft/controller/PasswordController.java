package edu.jxut.sft.controller;

import edu.jxut.sft.untils.DbUtil;
import edu.jxut.sft.untils.PasswordUtil;
import org.springframework.web.bind.annotation.*;

import javax.servlet.http.HttpSession;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;

/**
 * 密码修改 Controller
 */
@RestController
@RequestMapping("/user")
public class PasswordController {

    /**
     * 修改密码
     */
    @PostMapping("/changePassword")
    @ResponseBody
    public String changePassword(@RequestParam String oldPassword,
                                 @RequestParam String newPassword,
                                 HttpSession session) {
        String username = (String) session.getAttribute("username");
        if (username == null) {
            return "{\"error\":\"请先登录\"}";
        }

        if (oldPassword == null || oldPassword.trim().isEmpty()
                || newPassword == null || newPassword.trim().isEmpty()) {
            return "{\"error\":\"密码不能为空\"}";
        }

        try (Connection conn = DbUtil.getConnection()) {
            // 验证旧密码
            String sql = "SELECT password FROM user WHERE username = ?";
            try (PreparedStatement ps = conn.prepareStatement(sql)) {
                ps.setString(1, username);
                try (ResultSet rs = ps.executeQuery()) {
                    if (rs.next()) {
                        String storedHash = rs.getString("password");
                        if (!PasswordUtil.verify(oldPassword, storedHash)) {
                            return "{\"error\":\"旧密码不正确\"}";
                        }
                    } else {
                        return "{\"error\":\"用户不存在\"}";
                    }
                }
            }

            // 更新为新密码
            String updateSql = "UPDATE user SET password = ? WHERE username = ?";
            try (PreparedStatement ps = conn.prepareStatement(updateSql)) {
                ps.setString(1, PasswordUtil.encrypt(newPassword));
                ps.setString(2, username);
                int rows = ps.executeUpdate();
                if (rows > 0) {
                    return "{\"success\":\"密码修改成功，请重新登录\"}";
                }
                return "{\"error\":\"密码修改失败\"}";
            }
        } catch (Exception e) {
            e.printStackTrace();
            return "{\"error\":\"系统错误，请稍后重试\"}";
        }
    }
}
