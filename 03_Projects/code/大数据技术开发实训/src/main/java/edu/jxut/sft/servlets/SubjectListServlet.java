package edu.jxut.sft.servlets;

import com.alibaba.fastjson2.JSON;
import edu.jxut.sft.pojo.Subject;
import edu.jxut.sft.Service.SubjectService;
import edu.jxut.sft.Service.SubjectServiceImpl;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.List;

// @WebServlet("/subject/list")  // 已被 SubjectController 替代，禁用避免路由冲突
public class SubjectListServlet extends HttpServlet {

    private SubjectService subjectService = new SubjectServiceImpl();

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {
        req.setCharacterEncoding("UTF-8");
        resp.setContentType("application/json;charset=UTF-8");
        PrintWriter out = resp.getWriter();

        String subjectName = req.getParameter("name");

        try {
            List<Subject> subjects = subjectService.findSubjectsByName(subjectName);
            String json = JSON.toJSONString(subjects);
            out.write(json);
        } catch (Exception e) {
            e.printStackTrace();
            out.write("{\"error\":\"查询科目失败：" + e.getMessage().replace("\"", "\\\"") + "\"}");
        }
    }
}
