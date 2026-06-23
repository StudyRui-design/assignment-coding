package edu.jxut.sft.Service;

import edu.jxut.sft.dao.SubjectDao;
import edu.jxut.sft.dao.SubjectDaoImpl;
import edu.jxut.sft.pojo.Subject;
import edu.jxut.sft.Service.SubjectService;
import java.util.List;

public class SubjectServiceImpl implements SubjectService {

    private SubjectDao subjectDao = new SubjectDaoImpl();

    @Override
    public boolean addSubject(Subject subject) {
        // 参数校验（示例：科目名不能为空）
        if (subject.getName() == null || subject.getName().trim().isEmpty()) {
            return false;
        }
        return subjectDao.addSubject(subject) > 0;
    }

    @Override
    public boolean deleteSubject(Integer id) {
        // 校验id有效性
        if (id == null || id <= 0) {
            return false;
        }
        return subjectDao.deleteSubject(id) > 0;
    }

    @Override
    public boolean updateSubject(Subject subject) {
        // 校验id和科目名
        if (subject.getId() == null || subject.getId() <= 0
                || subject.getName() == null || subject.getName().trim().isEmpty()) {
            return false;
        }
        return subjectDao.updateSubject(subject) > 0;
    }

    @Override
    public List<Subject> findAllSubjects() {
        return subjectDao.findAllSubjects();
    }

    @Override
    public List<Subject> findSubjectsByName(String name) {
        // 若名称为空，查所有
        if (name == null || name.trim().isEmpty()) {
            return subjectDao.findAllSubjects();
        }
        return subjectDao.findSubjectsByName(name.trim());
    }
}