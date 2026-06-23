package edu.jxut.sft.controller;

import edu.jxut.sft.dto.ApiResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.web.bind.annotation.*;

import java.util.*;
import java.util.stream.Collectors;

/**
 * AI 智能助手控制器
 * 提供基于本地数据的智能问答（当 DeepSeek 等大模型 API 不可用时的降级方案）
 */
@RestController
@RequestMapping("/sft/ai")
public class AiChatController {

    @Autowired
    private JdbcTemplate jdbcTemplate;

    @PostMapping("/chat")
    public ApiResponse chat(@RequestBody Map<String, String> request) {
        String message = request.get("message");
        if (message == null || message.trim().isEmpty()) {
            return ApiResponse.error("消息不能为空");
        }

        String reply = generateReply(message.trim());
        Map<String, String> result = new HashMap<>();
        result.put("reply", reply);
        return ApiResponse.success(result);
    }

    private String generateReply(String msg) {
        String lower = msg.toLowerCase();

        // 系统使用相关
        if (lower.contains("怎么用") || lower.contains("使用") || lower.contains("操作")) {
            return "本系统是一个**大数据应用课件管理平台**，主要功能包括：\n\n" +
                   "① **科目管理** - 添加、编辑、查看课程科目\n" +
                   "② **课件管理** - 上传和管理学习课件\n" +
                   "③ **用户管理** - 管理系统用户信息\n" +
                   "④ **数据可视化** - 图表展示学习数据\n" +
                   "⑤ **大数据分析** - 基于Spark的实时统计分析\n" +
                   "⑥ **智能推荐** - AI推荐热门科目\n\n" +
                   "点击左侧导航栏即可使用各项功能。";
        }

        // 科目查询
        if (lower.contains("科目") || lower.contains("课程") || lower.contains("有哪些")) {
            List<Map<String, Object>> subjects = jdbcTemplate.queryForList(
                    "SELECT name, creator, status FROM subject ORDER BY id LIMIT 10");
            if (subjects.isEmpty()) {
                return "当前系统中暂未添加科目，你可以通过「科目管理」页面添加新科目。";
            }
            StringBuilder sb = new StringBuilder("当前系统包含以下科目：\n\n");
            for (int i = 0; i < subjects.size(); i++) {
                Map<String, Object> s = subjects.get(i);
                sb.append("**").append(i + 1).append(". ").append(s.get("name")).append("**");
                sb.append("（创建者：").append(s.get("creator")).append("，状态：").append(s.get("status")).append("）\n");
            }
            sb.append("\n更多科目请查看「科目管理」页面。");
            return sb.toString();
        }

        // 学习推荐
        if (lower.contains("推荐") || lower.contains("学什么") || lower.contains("建议")) {
            List<Map<String, Object>> hotSubjects = jdbcTemplate.queryForList(
                    "SELECT s.name, COUNT(st.id) AS cnt FROM subject s " +
                    "LEFT JOIN study st ON s.name = st.subject_name OR s.id = st.subject_id " +
                    "GROUP BY s.id, s.name ORDER BY cnt DESC LIMIT 5");
            if (hotSubjects.isEmpty() || hotSubjects.get(0).get("cnt") == null ||
                ((Number) hotSubjects.get(0).get("cnt")).longValue() == 0) {
                return "目前还没有足够的学习数据来生成推荐。建议你先浏览「科目管理」页面，选择感兴趣的科目开始学习！";
            }
            StringBuilder sb = new StringBuilder("根据当前学习数据，为你推荐以下热门科目：\n\n");
            for (int i = 0; i < hotSubjects.size(); i++) {
                Map<String, Object> s = hotSubjects.get(i);
                sb.append("⭐ **").append(s.get("name")).append("** - ")
                  .append(s.get("cnt")).append(" 人已学习\n");
            }
            sb.append("\n你也可以查看「智能推荐」页面获取更多个性化推荐。");
            return sb.toString();
        }

        // 大数据分析
        if (lower.contains("大数据") || lower.contains("spark") || lower.contains("分析")) {
            long userCount = jdbcTemplate.queryForObject("SELECT COUNT(*) FROM `user`", Long.class);
            long subjectCount = jdbcTemplate.queryForObject("SELECT COUNT(*) FROM subject", Long.class);
            long studyCount = jdbcTemplate.queryForObject("SELECT COUNT(*) FROM study", Long.class);
            return "**大数据分析平台概览**：\n\n" +
                   "👥 注册用户：**" + userCount + "** 人\n" +
                   "📚 课程科目：**" + subjectCount + "** 门\n" +
                   "📝 学习记录：**" + studyCount + "** 条\n" +
                   "📊 人均学习：**" + (userCount > 0 ? Math.round((double)studyCount/userCount * 10.0)/10.0 : 0) + "** 次\n\n" +
                   "系统基于 Apache Spark 进行实时数据统计分析，你可以在「大数据分析」页面查看详细图表。";
        }

        // 笑话
        if (lower.contains("笑话") || lower.contains("开心") || lower.contains("好玩")) {
            String[] jokes = {
                "程序员最讨厌康熙的哪个儿子？——胤禩，因为他是八阿哥（bug）。",
                "一个程序员在公园里散步，看到一只乌龟在爬，他说：'这个线程阻塞了。'",
                "SQL 查询走进一家酒吧，看到两张桌子，走过去问：'我可以 JOIN 你们吗？'",
                "为什么程序员总是分不清万圣节和圣诞节？因为 Oct 31 == Dec 25。"
            };
            return jokes[new Random().nextInt(jokes.length)];
        }

        // 默认回复
        return "你好！我是 AI 智能学习助手，可以帮你：\n\n" +
               "📖 **查询科目** - 输入「有哪些科目」\n" +
               "⭐ **学习推荐** - 输入「推荐学习什么」\n" +
               "📊 **数据概览** - 输入「大数据分析」\n" +
               "❓ **使用帮助** - 输入「怎么使用系统」\n" +
               "😄 **讲个笑话** - 输入「讲个笑话」\n\n" +
               "请告诉我你想了解什么吧！";
    }
}
