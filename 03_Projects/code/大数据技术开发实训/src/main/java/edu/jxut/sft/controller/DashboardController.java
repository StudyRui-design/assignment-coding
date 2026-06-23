package edu.jxut.sft.controller;

import com.alibaba.fastjson2.JSON;
import edu.jxut.sft.untils.DbUtil;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.util.HashMap;
import java.util.Map;

/**
 * 数据可视化统计 Controller
 */
@RestController
@RequestMapping("/dashboard")
public class DashboardController {

    /**
     * 获取统计数据（用户总数、科目总数、可用科目、禁用科目）
     */
    @GetMapping("/stats")
    public String getStats() {
        Map<String, Object> stats = new HashMap<>();
        try (Connection conn = DbUtil.getConnection()) {
            // 用户总数
            String userSql = "SELECT COUNT(*) FROM user";
            try (PreparedStatement ps = conn.prepareStatement(userSql);
                 ResultSet rs = ps.executeQuery()) {
                if (rs.next()) {
                    stats.put("userCount", rs.getInt(1));
                }
            }

            // 科目总数
            String subjectTotalSql = "SELECT COUNT(*) FROM subject";
            try (PreparedStatement ps = conn.prepareStatement(subjectTotalSql);
                 ResultSet rs = ps.executeQuery()) {
                if (rs.next()) {
                    stats.put("subjectCount", rs.getInt(1));
                }
            }

            // 可用科目数
            String activeSql = "SELECT COUNT(*) FROM subject WHERE status = '正常'";
            try (PreparedStatement ps = conn.prepareStatement(activeSql);
                 ResultSet rs = ps.executeQuery()) {
                if (rs.next()) {
                    stats.put("activeCount", rs.getInt(1));
                }
            }

            // 禁用科目数
            String inactiveSql = "SELECT COUNT(*) FROM subject WHERE status = '禁用'";
            try (PreparedStatement ps = conn.prepareStatement(inactiveSql);
                 ResultSet rs = ps.executeQuery()) {
                if (rs.next()) {
                    stats.put("inactiveCount", rs.getInt(1));
                }
            }

            return JSON.toJSONString(stats);
        } catch (Exception e) {
            e.printStackTrace();
            return "{\"error\":\"统计失败，请稍后重试\"}";
        }
    }
}
