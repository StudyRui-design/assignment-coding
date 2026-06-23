package edu.jxut.sft.Service;

import edu.jxut.sft.pojo.Study;
import java.util.List;

/**
 * 课件 Service 接口
 */
public interface StudyService {
    boolean addStudy(Study study);
    boolean deleteStudy(Integer id);
    boolean updateStudy(Study study);
    List<Study> findAllStudies();
    List<Study> findStudiesByName(String name);
    Study findStudyById(Integer id);
}
