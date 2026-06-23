package edu.jxut.sft.servlets;

import edu.jxut.sft.pojo.Subject;
import edu.jxut.sft.Service.SubjectService;
import edu.jxut.sft.Service.SubjectServiceImpl;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;

// @WebServlet("/subject/update")  // 已被 SubjectController 替代，禁用避免路由冲突
public class SubjectUpdateServlet extends HttpServlet {

    private SubjectService subjectService = new SubjectServiceImpl();

    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {
        req.setCharacterEncoding("UTF-8");

        String idStr = req.getParameter("id");
        String name = req.getParameter("name");
        String status = req.getParameter("status");

        try {
            Subject subject = new Subject();
            subject.setId(Integer.parseInt(idStr));
            subject.setName(name);
            subject.setStatus(status);

            boolean success = subjectService.updateSubject(subject);

            if (success) {
                resp.sendRedirect("/sft/subject/list");
            } else {
                resp.setContentType("text/html;charset=UTF-8");
                resp.getWriter().write(
                    "<script>alert('更新失败，请检查数据');history.back();</script>");
            }
        } catch (NumberFormatException e) {
            resp.setContentType("text/html;charset=UTF-8");
            resp.getWriter().write(
                "<script>alert('科目ID格式错误');history.back();</script>");
        }
    }
}