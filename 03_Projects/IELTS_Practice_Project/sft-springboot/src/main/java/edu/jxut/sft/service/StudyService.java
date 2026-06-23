package edu.jxut.sft.service;

import edu.jxut.sft.entity.Study;
import java.util.List;

public interface StudyService {
    boolean addStudy(Study study);
    boolean deleteStudy(Integer id);
    boolean updateStudy(Study study);
    Study findStudyById(Integer id);
    List<Study> findAllStudies();
    long getTotalCount();
    List<Study> findByPage(int page, int pageSize);
    List<Study> searchByKeyword(String keyword, int page, int pageSize);
    long getTotalCountByKeyword(String keyword);
}
