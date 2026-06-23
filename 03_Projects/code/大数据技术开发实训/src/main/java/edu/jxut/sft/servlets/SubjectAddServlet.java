package edu.jxut.sft.servlets;

import edu.jxut.sft.pojo.Subject;
import edu.jxut.sft.Service.SubjectService;
import edu.jxut.sft.Service.SubjectServiceImpl;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;
import java.io.IOException;

// @WebServlet("/subject/add")  // 已被 SubjectController 替代，禁用避免路由冲突
public class SubjectAddServlet extends HttpServlet {

    private SubjectService subjectService = new SubjectServiceImpl();

    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {
        req.setCharacterEncoding("UTF-8");

        String name = req.getParameter("name");
        String status = req.getParameter("status");

        // 从登录会话中获取当前用户名作为创建人
        HttpSession session = req.getSession();
        String creator = (String) session.getAttribute("username");
        if (creator == null || creator.isEmpty()) {
            creator = "admin";
        }

        Subject subject = new Subject();
        subject.setName(name);
        subject.setCreator(creator);
        subject.setStatus(status);

        boolean success = subjectService.addSubject(subject);

        if (success) {
            resp.sendRedirect("/sft/subject/list");
        } else {
            resp.setContentType("text/html;charset=UTF-8");
            resp.getWriter().write(
                "<script>alert('添加失败，科目名不能为空');history.back();</script>");
        }
    }
}