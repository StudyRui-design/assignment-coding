package edu.jxut.sft.service;

import edu.jxut.sft.entity.User;
import java.util.List;

public interface UserService {
    boolean addUser(User user);
    boolean deleteUser(Integer id);
    boolean updateUser(User user);
    User findUserById(Integer id);
    User findUserByUsername(String username);
    User login(String username, String password);
    boolean changePassword(Integer userId, String oldPassword, String newPassword);
    List<User> findAllUsers();
    List<User> findUsersByName(String realName);
    long getTotalCount();
    long getTotalCountByName(String realName);
    List<User> findByPage(int page, int pageSize);
    List<User> findByPageAndName(int page, int pageSize, String realName);
}
