package edu.jxut.sft.dao;

import edu.jxut.sft.dao.SubjectDao;
import edu.jxut.sft.pojo.Subject;
import edu.jxut.sft.untils.DbUtil;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.util.ArrayList;
import java.util.List;

public class SubjectDaoImpl implements SubjectDao {

    @Override
    public int addSubject(Subject subject) {
        String sql = "INSERT INTO subject (name, creator, status) VALUES (?, ?, ?)";
        try (Connection conn = DbUtil.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setString(1, subject.getName());
            ps.setString(2, subject.getCreator());
            ps.setString(3, subject.getStatus());
            return ps.executeUpdate(); // 返回影响行数（1表示成功）
        } catch (Exception e) {
            e.printStackTrace();
            return 0;
        }
    }

    @Override
    public int deleteSubject(Integer id) {
        String sql = "DELETE FROM subject WHERE id = ?";
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
    public int updateSubject(Subject subject) {
        String sql = "UPDATE subject SET name = ?, status = ? WHERE id = ?";
        try (Connection conn = DbUtil.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setString(1, subject.getName());
            ps.setString(2, subject.getStatus());
            ps.setInt(3, subject.getId());
            return ps.executeUpdate();
        } catch (Exception e) {
            e.printStackTrace();
            return 0;
        }
    }

    @Override
    public List<Subject> findAllSubjects() {
        List<Subject> subjects = new ArrayList<>();
        String sql = "SELECT * FROM subject";
        try (Connection conn = DbUtil.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql);
             ResultSet rs = ps.executeQuery()) {
            while (rs.next()) {
                Subject s = new Subject();
                s.setId(rs.getInt("id"));
                s.setName(rs.getString("name"));
                s.setCreator(rs.getString("creator"));
                s.setStatus(rs.getString("status"));
                subjects.add(s);
            }
            return subjects;
        } catch (Exception e) {
            e.printStackTrace();
            return subjects;
        }
    }

    @Override
    public List<Subject> findSubjectsByName(String name) {
        List<Subject> subjects = new ArrayList<>();
        String sql = "SELECT * FROM subject WHERE name LIKE ?";
        try (Connection conn = DbUtil.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setString(1, "%" + name + "%"); // 模糊查询
            ResultSet rs = ps.executeQuery();
            while (rs.next()) {
                Subject s = new Subject();
                s.setId(rs.getInt("id"));
                s.setName(rs.getString("name"));
                s.setCreator(rs.getString("creator"));
                s.setStatus(rs.getString("status"));
                subjects.add(s);
            }
            return subjects;
        } catch (Exception e) {
            e.printStackTrace();
            return subjects;
        }
    }
}