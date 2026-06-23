package edu.jxut.sft.Service;

import edu.jxut.sft.pojo.Subject;
import java.util.List;

public interface SubjectService {
    boolean addSubject(Subject subject);
    boolean deleteSubject(Integer id);
    boolean updateSubject(Subject subject);
    List<Subject> findAllSubjects();
    List<Subject> findSubjectsByName(String name);
}