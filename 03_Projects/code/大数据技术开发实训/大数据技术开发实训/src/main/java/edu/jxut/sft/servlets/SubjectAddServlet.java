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

@WebServlet("/subject/add")
public class SubjectAddServlet extends HttpServlet {

    private SubjectService subjectService = new SubjectServiceImpl();

    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        req.setCharacterEncoding("UTF-8"); // 处理中文乱码

        // 获取表单数据
        String name = req.getParameter("name");
        String creator = "admin"; // 示例：固定创建人为admin，实际可从登录态获取
        String status = req.getParameter("status");

        // 封装为Subject对象
        Subject subject = new Subject();
        subject.setName(name);
        subject.setCreator(creator);
        subject.setStatus(status);

        // 调用Service添加
        boolean success = subjectService.addSubject(subject);

        // 重定向回列表页（刷新显示新增结果）
        resp.sendRedirect("/sft/subject/list");
    }
}