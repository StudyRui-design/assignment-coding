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

@WebServlet("/subject/update")
public class SubjectUpdateServlet extends HttpServlet {

    private SubjectService subjectService = new SubjectServiceImpl();

    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        req.setCharacterEncoding("UTF-8"); // 处理中文乱码

        // 获取表单数据
        String idStr = req.getParameter("id");
        String name = req.getParameter("name");
        String status = req.getParameter("status");

        // 封装为Subject对象
        Subject subject = new Subject();
        subject.setId(Integer.parseInt(idStr)); // 转换为整数类型
        subject.setName(name);
        subject.setStatus(status);
        // 创建人通常不允许修改，无需重新设置

        // 调用Service更新
        boolean success = subjectService.updateSubject(subject);

        // 重定向回科目列表页
        resp.sendRedirect("/sft/subject/list");
    }
}