package edu.jxut.sft.repository;

import edu.jxut.sft.entity.Subject;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.jdbc.support.GeneratedKeyHolder;
import org.springframework.jdbc.support.KeyHolder;
import org.springframework.stereotype.Repository;

import java.sql.PreparedStatement;
import java.sql.Statement;
import java.util.List;

@Repository
public class SubjectRepository {

    @Autowired
    private JdbcTemplate jdbcTemplate;

    private final RowMapper<Subject> rowMapper = (rs, rowNum) -> {
        Subject s = new Subject();
        s.setId(rs.getInt("id"));
        s.setName(rs.getString("name"));
        s.setCreator(rs.getString("creator"));
        s.setStatus(rs.getString("status"));
        return s;
    };

    public int insertSubject(Subject subject) {
        String sql = "INSERT INTO subject (name, creator, status) VALUES (?, ?, ?)";
        KeyHolder keyHolder = new GeneratedKeyHolder();
        jdbcTemplate.update(connection -> {
            PreparedStatement ps = connection.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS);
            ps.setString(1, subject.getName());
            ps.setString(2, subject.getCreator());
            ps.setString(3, subject.getStatus());
            return ps;
        }, keyHolder);
        if (keyHolder.getKey() != null) {
            subject.setId(keyHolder.getKey().intValue());
        }
        return 1;
    }

    public int deleteSubject(Integer id) {
        return jdbcTemplate.update("DELETE FROM subject WHERE id = ?", id);
    }

    public int updateSubject(Subject subject) {
        String sql = "UPDATE subject SET name=?, status=? WHERE id=?";
        return jdbcTemplate.update(sql, subject.getName(), subject.getStatus(), subject.getId());
    }

    public Subject findSubjectById(Integer id) {
        List<Subject> list = jdbcTemplate.query("SELECT * FROM subject WHERE id=?", rowMapper, id);
        return list.isEmpty() ? null : list.get(0);
    }

    public List<Subject> findAllSubjects() {
        return jdbcTemplate.query("SELECT * FROM subject ORDER BY id DESC", rowMapper);
    }

    public long getTotalCount() {
        return jdbcTemplate.queryForObject("SELECT COUNT(*) FROM subject", Long.class);
    }

    public List<Subject> findByPage(int offset, int pageSize) {
        return jdbcTemplate.query("SELECT * FROM subject ORDER BY id DESC LIMIT ?, ?",
                rowMapper, offset, pageSize);
    }
}
