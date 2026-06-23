package edu.jxut.sft.dao;

import edu.jxut.sft.pojo.Subject;
import java.util.List;

public interface SubjectDao {
    // 新增科目
    int addSubject(Subject subject);
    // 删除科目（根据id）
    int deleteSubject(Integer id);
    // 修改科目（根据id）
    int updateSubject(Subject subject);
    // 查询所有科目
    List<Subject> findAllSubjects();
    // 按名称查询科目
    List<Subject> findSubjectsByName(String name);
}