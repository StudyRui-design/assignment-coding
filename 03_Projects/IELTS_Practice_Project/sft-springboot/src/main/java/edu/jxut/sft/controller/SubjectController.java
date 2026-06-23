package edu.jxut.sft.controller;

import edu.jxut.sft.dto.ApiResponse;
import edu.jxut.sft.entity.Subject;
import edu.jxut.sft.service.SubjectService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/sft/subject")
public class SubjectController {

    @Autowired
    private SubjectService subjectService;

    @GetMapping("/list")
    public ApiResponse list(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "6") int pageSize) {
        long total = subjectService.getTotalCount();
        List<Subject> subjects = subjectService.findByPage(page, pageSize);
        return ApiResponse.success(ApiResponse.pageData(subjects, total, page, pageSize));
    }

    @GetMapping("/all")
    public ApiResponse all() {
        return ApiResponse.success(subjectService.findAllSubjects());
    }

    @GetMapping("/{id}")
    public ApiResponse view(@PathVariable Integer id) {
        Subject subject = subjectService.findSubjectById(id);
        if (subject != null) {
            return ApiResponse.success(subject);
        }
        return ApiResponse.error("科目不存在");
    }

    @PostMapping("/add")
    public ApiResponse add(@RequestBody Subject subject) {
        boolean result = subjectService.addSubject(subject);
        if (result) {
            return ApiResponse.success("添加成功");
        }
        return ApiResponse.error("添加失败");
    }

    @PutMapping("/update")
    public ApiResponse update(@RequestBody Subject subject) {
        boolean result = subjectService.updateSubject(subject);
        if (result) {
            return ApiResponse.success("修改成功");
        }
        return ApiResponse.error("修改失败");
    }

    @DeleteMapping("/{id}")
    public ApiResponse delete(@PathVariable Integer id) {
        boolean result = subjectService.deleteSubject(id);
        if (result) {
            return ApiResponse.success("删除成功");
        }
        return ApiResponse.error("删除失败");
    }
}
