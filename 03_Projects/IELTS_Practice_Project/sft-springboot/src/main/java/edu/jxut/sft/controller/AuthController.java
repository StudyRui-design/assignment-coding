package edu.jxut.sft.controller;

import edu.jxut.sft.dto.ApiResponse;
import edu.jxut.sft.dto.LoginRequest;
import edu.jxut.sft.dto.PasswordRequest;
import edu.jxut.sft.entity.User;
import edu.jxut.sft.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import javax.servlet.http.HttpSession;

@RestController
@RequestMapping("/sft/auth")
public class AuthController {

    @Autowired
    private UserService userService;

    @PostMapping("/login")
    public ApiResponse login(@RequestBody LoginRequest request, HttpSession session) {
        if (request.getUsername() == null || request.getPassword() == null) {
            return ApiResponse.error("用户名和密码不能为空");
        }
        User user = userService.login(request.getUsername(), request.getPassword());
        if (user != null) {
            session.setAttribute("loginUser", user);
            return ApiResponse.success("登录成功", user);
        }
        return ApiResponse.error(401, "用户名或密码错误");
    }

    @PostMapping("/register")
    public ApiResponse register(@RequestBody User user) {
        boolean result = userService.addUser(user);
        if (result) {
            return ApiResponse.success("注册成功");
        }
        return ApiResponse.error("注册失败，用户名可能已存在");
    }

    @GetMapping("/logout")
    public ApiResponse logout(HttpSession session) {
        session.invalidate();
        return ApiResponse.success("已退出登录");
    }

    @GetMapping("/session")
    public ApiResponse getSessionUser(HttpSession session) {
        User user = (User) session.getAttribute("loginUser");
        if (user != null) {
            return ApiResponse.success(user);
        }
        return ApiResponse.unauthorized();
    }

    @PostMapping("/password")
    public ApiResponse changePassword(@RequestBody PasswordRequest request, HttpSession session) {
        User sessionUser = (User) session.getAttribute("loginUser");
        if (sessionUser == null) {
            return ApiResponse.unauthorized();
        }
        boolean result = userService.changePassword(
                sessionUser.getId(), request.getOldPassword(), request.getNewPassword());
        if (result) {
            return ApiResponse.success("密码修改成功");
        }
        return ApiResponse.error("旧密码错误");
    }
}
