package edu.jxut.sft.controller;

import edu.jxut.sft.dto.ApiResponse;
import edu.jxut.sft.entity.Study;
import edu.jxut.sft.service.StudyService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/sft/study")
public class StudyController {

    @Autowired
    private StudyService studyService;

    @GetMapping("/list")
    public ApiResponse list(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "6") int pageSize,
            @RequestParam(required = false) String keyword) {
        long total;
        List<Study> studies;
        if (keyword != null && !keyword.trim().isEmpty()) {
            total = studyService.getTotalCountByKeyword(keyword);
            studies = studyService.searchByKeyword(keyword, page, pageSize);
        } else {
            total = studyService.getTotalCount();
            studies = studyService.findByPage(page, pageSize);
        }
        return ApiResponse.success(ApiResponse.pageData(studies, total, page, pageSize));
    }

    @GetMapping("/{id}")
    public ApiResponse view(@PathVariable Integer id) {
        Study study = studyService.findStudyById(id);
        if (study != null) {
            return ApiResponse.success(study);
        }
        return ApiResponse.error("学习记录不存在");
    }

    @PostMapping("/add")
    public ApiResponse add(@RequestBody Study study) {
        boolean result = studyService.addStudy(study);
        if (result) {
            return ApiResponse.success("添加成功");
        }
        return ApiResponse.error("添加失败");
    }

    @PutMapping("/update")
    public ApiResponse update(@RequestBody Study study) {
        boolean result = studyService.updateStudy(study);
        if (result) {
            return ApiResponse.success("修改成功");
        }
        return ApiResponse.error("修改失败");
    }

    @DeleteMapping("/{id}")
    public ApiResponse delete(@PathVariable Integer id) {
        boolean result = studyService.deleteStudy(id);
        if (result) {
            return ApiResponse.success("删除成功");
        }
        return ApiResponse.error("删除失败");
    }
}
