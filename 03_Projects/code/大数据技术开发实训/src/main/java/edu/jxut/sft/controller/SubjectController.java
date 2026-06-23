package edu.jxut.sft.controller;

import com.alibaba.fastjson2.JSON;
import edu.jxut.sft.pojo.Subject;
import edu.jxut.sft.Service.SubjectService;
import edu.jxut.sft.Service.SubjectServiceImpl;
import org.springframework.web.bind.annotation.*;

import javax.servlet.http.HttpSession;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 科目管理 Controller
 */
@RestController
@RequestMapping("/subject")
public class SubjectController {

    private final SubjectService subjectService = new SubjectServiceImpl();

    /**
     * 查询科目列表（支持按名称模糊搜索）
     */
    @GetMapping("/list")
    public String list(@RequestParam(required = false) String name) {
        try {
            List<Subject> subjects = subjectService.findSubjectsByName(name);
            return JSON.toJSONString(subjects);
        } catch (Exception e) {
            e.printStackTrace();
            return "{\"error\":\"查询失败，请稍后重试\"}";
        }
    }

    /**
     * 添加科目
     */
    @PostMapping("/add")
    @ResponseBody
    public String add(@RequestParam String name,
                      @RequestParam String status,
                      HttpSession session) {
        String creator = (String) session.getAttribute("username");
        if (creator == null || creator.isEmpty()) {
            return "{\"error\":\"请先登录后再操作\"}";
        }
        try {
            Subject subject = new Subject();
            subject.setName(name);
            subject.setCreator(creator);
            subject.setStatus(status);

            boolean success = subjectService.addSubject(subject);
            if (success) {
                return "{\"success\":\"添加成功\"}";
            } else {
                return "{\"error\":\"添加失败，科目名不能为空\"}";
            }
        } catch (Exception e) {
            e.printStackTrace();
            return "{\"error\":\"添加失败，请稍后重试\"}";
        }
    }

    /**
     * 更新科目
     */
    @PostMapping("/update")
    @ResponseBody
    public String update(@RequestParam Integer id,
                         @RequestParam String name,
                         @RequestParam String status) {
        try {
            Subject subject = new Subject();
            subject.setId(id);
            subject.setName(name);
            subject.setStatus(status);

            boolean success = subjectService.updateSubject(subject);
            if (success) {
                return "{\"success\":\"更新成功\"}";
            } else {
                return "{\"error\":\"更新失败\"}";
            }
        } catch (Exception e) {
            e.printStackTrace();
            return "{\"error\":\"更新失败，请稍后重试\"}";
        }
    }

    /**
     * 删除科目
     */
    @GetMapping("/delete")
    public String delete(@RequestParam Integer id) {
        try {
            boolean success = subjectService.deleteSubject(id);
            if (success) {
                return "{\"success\":\"删除成功\"}";
            } else {
                return "{\"error\":\"未找到该科目\"}";
            }
        } catch (Exception e) {
            e.printStackTrace();
            return "{\"error\":\"删除失败，请稍后重试\"}";
        }
    }
}
