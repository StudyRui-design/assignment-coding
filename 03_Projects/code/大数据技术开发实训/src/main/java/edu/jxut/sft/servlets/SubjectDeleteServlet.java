package edu.jxut.sft.servlets;

import edu.jxut.sft.Service.SubjectService;
import edu.jxut.sft.Service.SubjectServiceImpl;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.io.PrintWriter;

// @WebServlet("/subject/delete")  // 已被 SubjectController 替代，禁用避免路由冲突
public class SubjectDeleteServlet extends HttpServlet {

    private SubjectService subjectService = new SubjectServiceImpl();

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {
        req.setCharacterEncoding("UTF-8");
        resp.setContentType("application/json;charset=UTF-8");
        PrintWriter out = resp.getWriter();

        String idStr = req.getParameter("id");

        if (idStr == null || idStr.trim().isEmpty()) {
            out.write("{\"error\":\"科目ID不能为空\"}");
            return;
        }

        try {
            int id = Integer.parseInt(idStr);
            boolean success = subjectService.deleteSubject(id);

            if (success) {
                out.write("{\"success\":\"删除成功\"}");
            } else {
                out.write("{\"error\":\"未找到该科目\"}");
            }
        } catch (NumberFormatException e) {
            out.write("{\"error\":\"科目ID格式错误\"}");
        } catch (Exception e) {
            e.printStackTrace();
            out.write("{\"error\":\"删除失败：" + e.getMessage().replace("\"", "\\\"") + "\"}");
        }
    }
}