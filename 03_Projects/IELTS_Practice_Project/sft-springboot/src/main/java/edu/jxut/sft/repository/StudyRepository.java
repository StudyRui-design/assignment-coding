package edu.jxut.sft.repository;

import edu.jxut.sft.entity.Study;
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
public class StudyRepository {

    @Autowired
    private JdbcTemplate jdbcTemplate;

    private final RowMapper<Study> rowMapper = (rs, rowNum) -> {
        Study s = new Study();
        s.setId(rs.getInt("id"));
        s.setTitle(rs.getString("title"));
        s.setSubjectId(rs.getObject("subject_id", Integer.class));
        s.setSubjectName(rs.getString("subject_name"));
        s.setSummary(rs.getString("summary"));
        s.setContent(rs.getString("content"));
        s.setFileSrc(rs.getString("file_src"));
        s.setCreator(rs.getString("creator"));
        s.setCreateTime(rs.getString("create_time"));
        return s;
    };

    public int insertStudy(Study study) {
        String sql = "INSERT INTO study (title, subject_id, subject_name, summary, content, file_src, creator) " +
                     "VALUES (?, ?, ?, ?, ?, ?, ?)";
        KeyHolder keyHolder = new GeneratedKeyHolder();
        jdbcTemplate.update(connection -> {
            PreparedStatement ps = connection.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS);
            ps.setString(1, study.getTitle());
            if (study.getSubjectId() != null) ps.setInt(2, study.getSubjectId());
            else ps.setNull(2, java.sql.Types.INTEGER);
            ps.setString(3, study.getSubjectName());
            ps.setString(4, study.getSummary());
            ps.setString(5, study.getContent());
            ps.setString(6, study.getFileSrc());
            ps.setString(7, study.getCreator());
            return ps;
        }, keyHolder);
        if (keyHolder.getKey() != null) {
            study.setId(keyHolder.getKey().intValue());
        }
        return 1;
    }

    public int deleteStudy(Integer id) {
        return jdbcTemplate.update("DELETE FROM study WHERE id = ?", id);
    }

    public int updateStudy(Study study) {
        String sql = "UPDATE study SET title=?, subject_id=?, subject_name=?, summary=?, content=?, file_src=? WHERE id=?";
        return jdbcTemplate.update(sql, study.getTitle(), study.getSubjectId(), study.getSubjectName(),
                study.getSummary(), study.getContent(), study.getFileSrc(), study.getId());
    }

    public Study findStudyById(Integer id) {
        List<Study> list = jdbcTemplate.query("SELECT * FROM study WHERE id=?", rowMapper, id);
        return list.isEmpty() ? null : list.get(0);
    }

    public List<Study> findAllStudies() {
        return jdbcTemplate.query("SELECT * FROM study ORDER BY id DESC", rowMapper);
    }

    public long getTotalCount() {
        return jdbcTemplate.queryForObject("SELECT COUNT(*) FROM study", Long.class);
    }

    public List<Study> findByPage(int offset, int pageSize) {
        return jdbcTemplate.query("SELECT * FROM study ORDER BY id DESC LIMIT ?, ?",
                rowMapper, offset, pageSize);
    }

    public List<Study> findByKeyword(String keyword, int offset, int pageSize) {
        String sql = "SELECT * FROM study WHERE title LIKE ? OR subject_name LIKE ? OR summary LIKE ? OR creator LIKE ? " +
                     "ORDER BY id DESC LIMIT ?, ?";
        String pattern = "%" + keyword + "%";
        return jdbcTemplate.query(sql, rowMapper, pattern, pattern, pattern, pattern, offset, pageSize);
    }

    public long getTotalCountByKeyword(String keyword) {
        String sql = "SELECT COUNT(*) FROM study WHERE title LIKE ? OR subject_name LIKE ? OR summary LIKE ? OR creator LIKE ?";
        String pattern = "%" + keyword + "%";
        return jdbcTemplate.queryForObject(sql, Long.class, pattern, pattern, pattern, pattern);
    }
}
