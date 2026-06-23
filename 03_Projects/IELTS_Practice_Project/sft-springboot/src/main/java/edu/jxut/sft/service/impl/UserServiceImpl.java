package edu.jxut.sft.service.impl;

import edu.jxut.sft.entity.User;
import edu.jxut.sft.repository.UserRepository;
import edu.jxut.sft.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.security.MessageDigest;
import java.util.List;

@Service
public class UserServiceImpl implements UserService {

    @Autowired
    private UserRepository userRepository;

    private final BCryptPasswordEncoder passwordEncoder = new BCryptPasswordEncoder();

    /** 判断是否为 MD5 哈希（32位十六进制） */
    private boolean isMd5Hash(String password) {
        return password != null && password.matches("^[a-f0-9]{32}$");
    }

    /** MD5 加密（兼容旧系统） */
    private String md5(String input) {
        if (input == null || input.isEmpty()) return "";
        try {
            MessageDigest md = MessageDigest.getInstance("MD5");
            byte[] digest = md.digest(input.getBytes("UTF-8"));
            StringBuilder sb = new StringBuilder();
            for (byte b : digest) sb.append(String.format("%02x", b & 0xff));
            return sb.toString();
        } catch (Exception e) {
            e.printStackTrace();
            return input;
        }
    }

    @Override
    @Transactional
    public boolean addUser(User user) {
        if (user.getUsername() == null || user.getUsername().trim().isEmpty()) return false;
        if (userRepository.findUserByUsername(user.getUsername()) != null) return false;
        if (user.getPassword() != null && !user.getPassword().isEmpty()) {
            user.setPassword(passwordEncoder.encode(user.getPassword()));
        }
        return userRepository.insertUser(user) > 0;
    }

    @Override
    @Transactional
    public boolean deleteUser(Integer id) {
        if (id == null || id <= 0) return false;
        return userRepository.deleteUser(id) > 0;
    }

    @Override
    @Transactional
    public boolean updateUser(User user) {
        if (user.getId() == null || user.getId() <= 0) return false;
        return userRepository.updateUser(user) > 0;
    }

    @Override
    public User findUserById(Integer id) {
        return userRepository.findUserById(id);
    }

    @Override
    public User findUserByUsername(String username) {
        return userRepository.findUserByUsername(username);
    }

    @Override
    public User login(String username, String password) {
        User user = userRepository.findUserByUsername(username);
        if (user == null) return null;

        String storedPassword = user.getPassword();

        // 1) BCrypt 验证（新系统）
        if (passwordEncoder.matches(password, storedPassword)) {
            user.setPassword(null);
            return user;
        }

        // 2) 兼容旧系统 MD5 密码
        if (isMd5Hash(storedPassword) && storedPassword.equalsIgnoreCase(md5(password))) {
            // 升级为 BCrypt 并更新数据库
            userRepository.updatePassword(user.getId(), passwordEncoder.encode(password));
            user.setPassword(null);
            return user;
        }

        return null;
    }

    @Override
    @Transactional
    public boolean changePassword(Integer userId, String oldPassword, String newPassword) {
        User user = userRepository.findUserById(userId);
        if (user == null) return false;

        String storedPassword = user.getPassword();

        // 验证旧密码（兼容 BCrypt 和 MD5）
        boolean match = passwordEncoder.matches(oldPassword, storedPassword);
        if (!match && isMd5Hash(storedPassword)) {
            match = storedPassword.equalsIgnoreCase(md5(oldPassword));
        }
        if (!match) return false;

        userRepository.updatePassword(userId, passwordEncoder.encode(newPassword));
        return true;
    }

    @Override
    public List<User> findAllUsers() {
        return userRepository.findAllUsers();
    }

    @Override
    public List<User> findUsersByName(String realName) {
        if (realName == null || realName.trim().isEmpty()) return userRepository.findAllUsers();
        return userRepository.findUsersByName(realName.trim());
    }

    @Override
    public long getTotalCount() {
        return userRepository.getTotalCount();
    }

    @Override
    public long getTotalCountByName(String realName) {
        if (realName == null || realName.trim().isEmpty()) return userRepository.getTotalCount();
        return userRepository.getTotalCountByName(realName.trim());
    }

    @Override
    public List<User> findByPage(int page, int pageSize) {
        return userRepository.findByPage((page - 1) * pageSize, pageSize);
    }

    @Override
    public List<User> findByPageAndName(int page, int pageSize, String realName) {
        if (realName == null || realName.trim().isEmpty()) {
            return userRepository.findByPage((page - 1) * pageSize, pageSize);
        }
        return userRepository.findByPageAndName(realName.trim(), (page - 1) * pageSize, pageSize);
    }
}
