package edu.jxut.sft.dao;

import edu.jxut.sft.pojo.Study;
import java.util.List;

/**
 * 课件 DAO 接口
 */
public interface StudyDao {
    int addStudy(Study study);
    int deleteStudy(Integer id);
    int updateStudy(Study study);
    List<Study> findAllStudies();
    List<Study> findStudiesByName(String name);
    Study findStudyById(Integer id);
}
