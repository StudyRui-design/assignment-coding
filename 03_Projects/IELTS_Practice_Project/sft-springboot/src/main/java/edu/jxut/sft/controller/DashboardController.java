package edu.jxut.sft.controller;

import edu.jxut.sft.dto.ApiResponse;
import edu.jxut.sft.repository.StudyRepository;
import edu.jxut.sft.repository.SubjectRepository;
import edu.jxut.sft.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.jdbc.core.JdbcTemplate;

import java.util.*;

@RestController
@RequestMapping("/sft/dashboard")
public class DashboardController {

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private SubjectRepository subjectRepository;

    @Autowired
    private StudyRepository studyRepository;

    @Autowired
    private JdbcTemplate jdbcTemplate;

    @GetMapping("/stats")
    public ApiResponse stats() {
        Map<String, Object> stats = new HashMap<>();

        // 基础统计
        long userCount = userRepository.getTotalCount();
        long subjectCount = subjectRepository.getTotalCount();
        long studyCount = studyRepository.getTotalCount();

        // 科目状态分布
        Map<String, Long> subjectStatus = new LinkedHashMap<>();
        try {
            List<Map<String, Object>> statusRows = jdbcTemplate.queryForList(
                "SELECT IFNULL(status,'未知') AS st, COUNT(*) AS cnt FROM subject GROUP BY status");
            for (Map<String, Object> row : statusRows) {
                subjectStatus.put(String.valueOf(row.get("st")), ((Number) row.get("cnt")).longValue());
            }
            if (subjectStatus.isEmpty()) subjectStatus.put("暂无数据", 0L);
        } catch (Exception e) {
            subjectStatus.put("查询失败", 0L);
        }
        long available = subjectStatus.getOrDefault("正常", 0L) + subjectStatus.getOrDefault("启用", 0L)
                       + subjectStatus.getOrDefault("1", 0L) + subjectStatus.getOrDefault("active", 0L);
        long disabled = subjectCount - available;
        if (disabled < 0) disabled = 0;

        // 用户类型分布
        Map<String, Long> userType = new LinkedHashMap<>();
        try {
            List<Map<String, Object>> typeRows = jdbcTemplate.queryForList(
                "SELECT IFNULL(user_type,'普通用户') AS ut, COUNT(*) AS cnt FROM user GROUP BY user_type");
            for (Map<String, Object> row : typeRows) {
                String key = String.valueOf(row.get("ut"));
                if ("null".equals(key)) key = "未分类";
                userType.put(key, ((Number) row.get("cnt")).longValue());
            }
            if (userType.isEmpty()) userType.put("暂无数据", 0L);
        } catch (Exception e) {
            userType.put("暂无数据", 0L);
        }

        stats.put("userCount", userCount);
        stats.put("subjectCount", subjectCount);
        stats.put("studyCount", studyCount);
        stats.put("ratingCount", 0);
        stats.put("availableCount", available);
        stats.put("disabledCount", disabled);
        stats.put("subjectStatus", subjectStatus);
        stats.put("userType", userType);

        return ApiResponse.success(stats);
    }
}
