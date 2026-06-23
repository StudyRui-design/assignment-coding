package edu.jxut.sft.controller;

import com.alibaba.fastjson2.JSON;
import edu.jxut.sft.pojo.Study;
import edu.jxut.sft.Service.StudyService;
import edu.jxut.sft.Service.StudyServiceImpl;
import org.springframework.web.bind.annotation.*;

import javax.servlet.http.HttpSession;

/**
 * 课件管理 Controller
 */
@RestController
@RequestMapping("/study")
public class StudyController {

    private final StudyService studyService = new StudyServiceImpl();

    /**
     * 查询课件列表（支持按名称模糊搜索）
     */
    @GetMapping("/list")
    public String list(@RequestParam(required = false) String name) {
        try {
            return JSON.toJSONString(studyService.findStudiesByName(name));
        } catch (Exception e) {
            e.printStackTrace();
            return "{\"error\":\"查询失败，请稍后重试\"}";
        }
    }

    /**
     * 查询课件详情
     */
    @GetMapping("/view")
    public String view(@RequestParam Integer id) {
        try {
            Study study = studyService.findStudyById(id);
            if (study != null) {
                return JSON.toJSONString(study);
            }
            return "{\"error\":\"课件不存在\"}";
        } catch (Exception e) {
            e.printStackTrace();
            return "{\"error\":\"查询失败，请稍后重试\"}";
        }
    }

    /**
     * 添加课件
     */
    @PostMapping("/add")
    @ResponseBody
    public String add(@RequestParam String name,
                      @RequestParam String subjectName,
                      @RequestParam String description,
                      @RequestParam String detail,
                      @RequestParam(required = false) String filePath,
                      HttpSession session) {
        try {
            String creator = (String) session.getAttribute("username");
            if (creator == null || creator.isEmpty()) {
                return "{\"error\":\"请先登录后再操作\"}";
            }

            Study study = new Study();
            study.setName(name);
            study.setSubjectName(subjectName);
            study.setDescription(description);
            study.setDetail(detail);
            study.setFilePath(filePath);
            study.setCreator(creator);

            boolean success = studyService.addStudy(study);
            if (success) {
                return "{\"success\":\"添加成功\"}";
            }
            return "{\"error\":\"添加失败\"}";
        } catch (Exception e) {
            e.printStackTrace();
            return "{\"error\":\"添加失败，请稍后重试\"}";
        }
    }

    /**
     * 更新课件
     */
    @PostMapping("/update")
    @ResponseBody
    public String update(@RequestParam Integer id,
                         @RequestParam String name,
                         @RequestParam String subjectName,
                         @RequestParam String description,
                         @RequestParam String detail,
                         @RequestParam(required = false) String filePath) {
        try {
            Study study = new Study();
            study.setId(id);
            study.setName(name);
            study.setSubjectName(subjectName);
            study.setDescription(description);
            study.setDetail(detail);
            study.setFilePath(filePath);

            boolean success = studyService.updateStudy(study);
            if (success) {
                return "{\"success\":\"更新成功\"}";
            }
            return "{\"error\":\"更新失败\"}";
        } catch (Exception e) {
            e.printStackTrace();
            return "{\"error\":\"更新失败，请稍后重试\"}";
        }
    }

    /**
     * 删除课件
     */
    @GetMapping("/delete")
    public String delete(@RequestParam Integer id) {
        try {
            boolean success = studyService.deleteStudy(id);
            if (success) {
                return "{\"success\":\"删除成功\"}";
            }
            return "{\"error\":\"未找到该课件\"}";
        } catch (Exception e) {
            e.printStackTrace();
            return "{\"error\":\"删除失败，请稍后重试\"}";
        }
    }
}
