package edu.jxut.sft.dao;

import edu.jxut.sft.pojo.Study;
import edu.jxut.sft.untils.DbUtil;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.List;

/**
 * 课件 DAO 实现类
 */
public class StudyDaoImpl implements StudyDao {

    @Override
    public int addStudy(Study study) {
        String sql = "INSERT INTO study (name, subject_name, description, detail, file_path, creator) VALUES (?, ?, ?, ?, ?, ?)";
        try (Connection conn = DbUtil.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS)) {
            ps.setString(1, study.getName());
            ps.setString(2, study.getSubjectName());
            ps.setString(3, study.getDescription());
            ps.setString(4, study.getDetail());
            ps.setString(5, study.getFilePath());
            ps.setString(6, study.getCreator());
            return ps.executeUpdate();
        } catch (Exception e) {
            e.printStackTrace();
            return 0;
        }
    }

    @Override
    public int deleteStudy(Integer id) {
        String sql = "DELETE FROM study WHERE id = ?";
        try (Connection conn = DbUtil.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setInt(1, id);
            return ps.executeUpdate();
        } catch (Exception e) {
            e.printStackTrace();
            return 0;
        }
    }

    @Override
    public int updateStudy(Study study) {
        String sql = "UPDATE study SET name = ?, subject_name = ?, description = ?, detail = ?, file_path = ? WHERE id = ?";
        try (Connection conn = DbUtil.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setString(1, study.getName());
            ps.setString(2, study.getSubjectName());
            ps.setString(3, study.getDescription());
            ps.setString(4, study.getDetail());
            ps.setString(5, study.getFilePath());
            ps.setInt(6, study.getId());
            return ps.executeUpdate();
        } catch (Exception e) {
            e.printStackTrace();
            return 0;
        }
    }

    @Override
    public List<Study> findAllStudies() {
        List<Study> studies = new ArrayList<>();
        String sql = "SELECT * FROM study ORDER BY id DESC";
        try (Connection conn = DbUtil.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql);
             ResultSet rs = ps.executeQuery()) {
            while (rs.next()) {
                studies.add(mapStudy(rs));
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return studies;
    }

    @Override
    public List<Study> findStudiesByName(String name) {
        List<Study> studies = new ArrayList<>();
        String sql = "SELECT * FROM study WHERE name LIKE ? ORDER BY id DESC";
        try (Connection conn = DbUtil.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setString(1, "%" + name + "%");
            try (ResultSet rs = ps.executeQuery()) {
                while (rs.next()) {
                    studies.add(mapStudy(rs));
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return studies;
    }

    @Override
    public Study findStudyById(Integer id) {
        String sql = "SELECT * FROM study WHERE id = ?";
        try (Connection conn = DbUtil.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setInt(1, id);
            try (ResultSet rs = ps.executeQuery()) {
                if (rs.next()) {
                    return mapStudy(rs);
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return null;
    }

    private Study mapStudy(ResultSet rs) throws Exception {
        Study s = new Study();
        s.setId(rs.getInt("id"));
        s.setName(rs.getString("name"));
        s.setSubjectName(rs.getString("subject_name"));
        s.setDescription(rs.getString("description"));
        s.setDetail(rs.getString("detail"));
        s.setFilePath(rs.getString("file_path"));
        s.setCreator(rs.getString("creator"));
        s.setCreateTime(rs.getString("create_time"));
        return s;
    }
}
