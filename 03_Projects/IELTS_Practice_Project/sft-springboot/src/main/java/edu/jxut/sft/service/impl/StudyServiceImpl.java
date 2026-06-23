package edu.jxut.sft.service.impl;

import edu.jxut.sft.entity.Study;
import edu.jxut.sft.repository.StudyRepository;
import edu.jxut.sft.service.StudyService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
public class StudyServiceImpl implements StudyService {

    @Autowired
    private StudyRepository studyRepository;

    @Override
    @Transactional
    public boolean addStudy(Study study) {
        if (study.getTitle() == null || study.getTitle().trim().isEmpty()) return false;
        return studyRepository.insertStudy(study) > 0;
    }

    @Override
    @Transactional
    public boolean deleteStudy(Integer id) {
        if (id == null || id <= 0) return false;
        return studyRepository.deleteStudy(id) > 0;
    }

    @Override
    @Transactional
    public boolean updateStudy(Study study) {
        if (study.getId() == null || study.getId() <= 0) return false;
        return studyRepository.updateStudy(study) > 0;
    }

    @Override
    public Study findStudyById(Integer id) {
        return studyRepository.findStudyById(id);
    }

    @Override
    public List<Study> findAllStudies() {
        return studyRepository.findAllStudies();
    }

    @Override
    public long getTotalCount() {
        return studyRepository.getTotalCount();
    }

    @Override
    public List<Study> findByPage(int page, int pageSize) {
        return studyRepository.findByPage((page - 1) * pageSize, pageSize);
    }

    @Override
    public List<Study> searchByKeyword(String keyword, int page, int pageSize) {
        return studyRepository.findByKeyword(keyword, (page - 1) * pageSize, pageSize);
    }

    @Override
    public long getTotalCountByKeyword(String keyword) {
        return studyRepository.getTotalCountByKeyword(keyword);
    }
}
