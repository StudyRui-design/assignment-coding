package edu.jxut.sft.service.impl;

import edu.jxut.sft.entity.Subject;
import edu.jxut.sft.repository.SubjectRepository;
import edu.jxut.sft.service.SubjectService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
public class SubjectServiceImpl implements SubjectService {

    @Autowired
    private SubjectRepository subjectRepository;

    @Override
    @Transactional
    public boolean addSubject(Subject subject) {
        if (subject.getName() == null || subject.getName().trim().isEmpty()) return false;
        return subjectRepository.insertSubject(subject) > 0;
    }

    @Override
    @Transactional
    public boolean deleteSubject(Integer id) {
        if (id == null || id <= 0) return false;
        return subjectRepository.deleteSubject(id) > 0;
    }

    @Override
    @Transactional
    public boolean updateSubject(Subject subject) {
        if (subject.getId() == null || subject.getId() <= 0) return false;
        return subjectRepository.updateSubject(subject) > 0;
    }

    @Override
    public Subject findSubjectById(Integer id) {
        return subjectRepository.findSubjectById(id);
    }

    @Override
    public List<Subject> findAllSubjects() {
        return subjectRepository.findAllSubjects();
    }

    @Override
    public long getTotalCount() {
        return subjectRepository.getTotalCount();
    }

    @Override
    public List<Subject> findByPage(int page, int pageSize) {
        return subjectRepository.findByPage((page - 1) * pageSize, pageSize);
    }
}
