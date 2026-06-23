package edu.jxut.sft.Service;

import edu.jxut.sft.dao.StudyDao;
import edu.jxut.sft.dao.StudyDaoImpl;
import edu.jxut.sft.pojo.Study;
import java.util.List;

/**
 * 课件 Service 实现类
 */
public class StudyServiceImpl implements StudyService {

    private final StudyDao studyDao = new StudyDaoImpl();

    @Override
    public boolean addStudy(Study study) {
        if (study.getName() == null || study.getName().trim().isEmpty()) {
            return false;
        }
        return studyDao.addStudy(study) > 0;
    }

    @Override
    public boolean deleteStudy(Integer id) {
        if (id == null || id <= 0) {
            return false;
        }
        return studyDao.deleteStudy(id) > 0;
    }

    @Override
    public boolean updateStudy(Study study) {
        if (study.getId() == null || study.getId() <= 0
                || study.getName() == null || study.getName().trim().isEmpty()) {
            return false;
        }
        return studyDao.updateStudy(study) > 0;
    }

    @Override
    public List<Study> findAllStudies() {
        return studyDao.findAllStudies();
    }

    @Override
    public List<Study> findStudiesByName(String name) {
        if (name == null || name.trim().isEmpty()) {
            return studyDao.findAllStudies();
        }
        return studyDao.findStudiesByName(name.trim());
    }

    @Override
    public Study findStudyById(Integer id) {
        return studyDao.findStudyById(id);
    }
}
