package edu.jxut.sft.servlets;

import edu.jxut.sft.pojo.Subject;
import edu.jxut.sft.Service.SubjectService;
import edu.jxut.sft.Service.SubjectServiceImpl;
import edu.jxut.sft.untils.DbUtil;
import com.alibaba.fastjson.JSON;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.io.PrintWriter;
import java.sql.Connection;
import java.util.List;

@WebServlet("/subject/list")
public class SubjectListServlet extends HttpServlet {

    private SubjectService subjectService = new SubjectServiceImpl();

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        // 1. 处理请求参数的中文乱码
        req.setCharacterEncoding("UTF-8");
        // 设置响应内容类型及编码，确保返回的中文数据不乱码
        resp.setContentType("application/json;charset=UTF-8");
        PrintWriter out = resp.getWriter();

        // 2. 获取查询参数（科目名）
        String subjectName = req.getParameter("name");

        // 3. 打印获取到的参数，验证数据传递
        System.out.println("=== 前端传递的科目查询参数 ===");
        System.out.println("科目名（name）：" + (subjectName == null ? "空（查询所有科目）" : subjectName));
        System.out.println("============================");

        // 4. 查询科目列表
        try (Connection conn = DbUtil.getConnection()) {
            System.out.println("数据库连接：" + conn);
            List<Subject> subjects = subjectService.findSubjectsByName(subjectName);

            // 打印查询结果，验证数据库操作
            System.out.println("=== 查询到的科目列表 ===");
            for (Subject subject : subjects) {
                System.out.println("科目编码：" + subject.getId() + "，科目名称：" + subject.getName() +
                        "，创建人：" + subject.getCreator() + "，状态：" + subject.getStatus());
            }
            System.out.println("=========================");

            // 5. 转换为JSON格式返回给前端
            String json = JSON.toJSONString(subjects);
            out.write(json);

        } catch (Exception e) {
            // 打印异常，方便排查问题
            e.printStackTrace();
            // 返回异常提示的JSON（保持响应格式统一）
            out.write("{\"error\":\"查询科目失败：" + e.getMessage().replace("\"", "\\\"") + "\"}");
        }
    }
}
