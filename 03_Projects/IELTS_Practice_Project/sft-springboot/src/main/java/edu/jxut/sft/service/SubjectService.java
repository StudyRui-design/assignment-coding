package edu.jxut.sft.service;

import edu.jxut.sft.entity.Subject;
import java.util.List;

public interface SubjectService {
    boolean addSubject(Subject subject);
    boolean deleteSubject(Integer id);
    boolean updateSubject(Subject subject);
    Subject findSubjectById(Integer id);
    List<Subject> findAllSubjects();
    long getTotalCount();
    List<Subject> findByPage(int page, int pageSize);
}
