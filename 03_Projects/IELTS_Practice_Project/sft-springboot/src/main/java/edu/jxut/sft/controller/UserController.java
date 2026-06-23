package edu.jxut.sft.controller;

import edu.jxut.sft.dto.ApiResponse;
import edu.jxut.sft.entity.User;
import edu.jxut.sft.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import javax.servlet.http.HttpSession;
import java.util.List;

@RestController
@RequestMapping("/sft/user")
public class UserController {

    @Autowired
    private UserService userService;

    @GetMapping("/list")
    public ApiResponse list(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "6") int pageSize,
            @RequestParam(required = false) String name) {
        long total;
        List<User> users;
        if (name != null && !name.trim().isEmpty()) {
            total = userService.getTotalCountByName(name);
            users = userService.findByPageAndName(page, pageSize, name);
        } else {
            total = userService.getTotalCount();
            users = userService.findByPage(page, pageSize);
        }
        return ApiResponse.success(ApiResponse.pageData(users, total, page, pageSize));
    }

    @GetMapping("/{id}")
    public ApiResponse view(@PathVariable Integer id) {
        User user = userService.findUserById(id);
        if (user != null) {
            user.setPassword(null);
            return ApiResponse.success(user);
        }
        return ApiResponse.error("用户不存在");
    }

    @PostMapping("/add")
    public ApiResponse add(@RequestBody User user) {
        boolean result = userService.addUser(user);
        if (result) {
            return ApiResponse.success("添加成功");
        }
        return ApiResponse.error("添加失败，用户名可能已存在");
    }

    @PutMapping("/update")
    public ApiResponse update(@RequestBody User user) {
        boolean result = userService.updateUser(user);
        if (result) {
            return ApiResponse.success("修改成功");
        }
        return ApiResponse.error("修改失败");
    }

    @DeleteMapping("/{id}")
    public ApiResponse delete(@PathVariable Integer id) {
        boolean result = userService.deleteUser(id);
        if (result) {
            return ApiResponse.success("删除成功");
        }
        return ApiResponse.error("删除失败");
    }
}
