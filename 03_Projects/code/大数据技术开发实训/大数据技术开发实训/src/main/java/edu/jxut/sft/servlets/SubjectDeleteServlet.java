package edu.jxut.sft.servlets;



import edu.jxut.sft.Service.SubjectService;
import edu.jxut.sft.Service.SubjectServiceImpl;
import edu.jxut.sft.pojo.Subject;
import edu.jxut.sft.untils.DbUtil;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.io.PrintWriter;
import java.sql.Connection;
import java.util.List;


@WebServlet("/subject/delete")
public class SubjectDeleteServlet extends HttpServlet {

    private SubjectService subjectService = new SubjectServiceImpl();

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        // 处理请求参数的中文乱码
        req.setCharacterEncoding("UTF-8");
        // 设置响应内容类型及编码
        resp.setContentType("text/html;charset=UTF-8");
        PrintWriter out = resp.getWriter();

        // 获取删除的科目ID
        String idStr = req.getParameter("id");
        System.out.println("=== 前端传递的删除参数 ===");
        System.out.println("科目ID（id）：" + (idStr == null ? "空" : idStr));
        System.out.println("========================");

        // 验证ID参数
        if (idStr == null || idStr.trim().isEmpty()) {
            out.write("{\"error\":\"删除失败：科目ID不能为空\"}");
            return;
        }

        try {
            int id = Integer.parseInt(idStr);
            // 执行删除操作
            try (Connection conn = DbUtil.getConnection()) {
                System.out.println("数据库连接：" + conn);
                boolean success = subjectService.deleteSubject(id);



                if (success) {
                    System.out.println("科目ID：" + id + " 删除成功");
                    out.write("{\"success\":\"删除成功\"}");
                } else {
                    System.out.println("科目ID：" + id + " 删除失败，未找到该科目");
                    out.write("{\"error\":\"删除失败：未找到该科目\"}");
                }
            }
        } catch (NumberFormatException e) {
            System.out.println("科目ID格式错误：" + idStr);
            out.write("{\"error\":\"删除失败：科目ID格式错误\"}");
        } catch (Exception e) {
            e.printStackTrace();
            out.write("{\"error\":\"删除失败：" + e.getMessage().replace("\"", "\\\"") + "\"}");
        }
    }
}