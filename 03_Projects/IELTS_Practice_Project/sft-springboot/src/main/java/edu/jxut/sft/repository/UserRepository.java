package edu.jxut.sft.repository;

import edu.jxut.sft.entity.User;
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
public class UserRepository {

    @Autowired
    private JdbcTemplate jdbcTemplate;

    private final RowMapper<User> rowMapper = (rs, rowNum) -> {
        User u = new User();
        u.setId(rs.getInt("id"));
        u.setUsername(rs.getString("username"));
        u.setPassword(rs.getString("password"));
        u.setRealName(rs.getString("real_name"));
        u.setGender(rs.getString("gender"));
        u.setBirth(rs.getString("birth"));
        u.setPhone(rs.getString("phone"));
        u.setAddress(rs.getString("address"));
        u.setUserType(rs.getString("user_type"));
        u.setCreateTime(rs.getString("create_time"));
        return u;
    };

    public int insertUser(User user) {
        String sql = "INSERT INTO user (username, password, real_name, gender, birth, phone, address, user_type) " +
                     "VALUES (?, ?, ?, ?, ?, ?, ?, ?)";
        KeyHolder keyHolder = new GeneratedKeyHolder();
        jdbcTemplate.update(connection -> {
            PreparedStatement ps = connection.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS);
            ps.setString(1, user.getUsername());
            ps.setString(2, user.getPassword());
            ps.setString(3, user.getRealName());
            ps.setString(4, user.getGender());
            ps.setString(5, user.getBirth());
            ps.setString(6, user.getPhone());
            ps.setString(7, user.getAddress());
            ps.setString(8, user.getUserType());
            return ps;
        }, keyHolder);
        if (keyHolder.getKey() != null) {
            user.setId(keyHolder.getKey().intValue());
        }
        return 1;
    }

    public int deleteUser(Integer id) {
        return jdbcTemplate.update("DELETE FROM user WHERE id = ?", id);
    }

    public int updateUser(User user) {
        String sql = "UPDATE user SET real_name=?, gender=?, birth=?, phone=?, address=?, user_type=? WHERE id=?";
        return jdbcTemplate.update(sql, user.getRealName(), user.getGender(), user.getBirth(),
                user.getPhone(), user.getAddress(), user.getUserType(), user.getId());
    }

    public int updatePassword(Integer id, String password) {
        return jdbcTemplate.update("UPDATE user SET password=? WHERE id=?", password, id);
    }

    public User findUserById(Integer id) {
        List<User> list = jdbcTemplate.query("SELECT * FROM user WHERE id=?", rowMapper, id);
        return list.isEmpty() ? null : list.get(0);
    }

    public User findUserByUsername(String username) {
        List<User> list = jdbcTemplate.query("SELECT * FROM user WHERE username=?", rowMapper, username);
        return list.isEmpty() ? null : list.get(0);
    }

    public List<User> findAllUsers() {
        return jdbcTemplate.query("SELECT * FROM user ORDER BY id DESC", rowMapper);
    }

    public List<User> findUsersByName(String realName) {
        return jdbcTemplate.query(
                "SELECT * FROM user WHERE real_name LIKE ? ORDER BY id DESC",
                rowMapper, "%" + realName + "%");
    }

    public long getTotalCount() {
        return jdbcTemplate.queryForObject("SELECT COUNT(*) FROM user", Long.class);
    }

    public long getTotalCountByName(String realName) {
        return jdbcTemplate.queryForObject(
                "SELECT COUNT(*) FROM user WHERE real_name LIKE ?", Long.class, "%" + realName + "%");
    }

    public List<User> findByPage(int offset, int pageSize) {
        return jdbcTemplate.query("SELECT * FROM user ORDER BY id DESC LIMIT ?, ?",
                rowMapper, offset, pageSize);
    }

    public List<User> findByPageAndName(String realName, int offset, int pageSize) {
        return jdbcTemplate.query(
                "SELECT * FROM user WHERE real_name LIKE ? ORDER BY id DESC LIMIT ?, ?",
                rowMapper, "%" + realName + "%", offset, pageSize);
    }
}
