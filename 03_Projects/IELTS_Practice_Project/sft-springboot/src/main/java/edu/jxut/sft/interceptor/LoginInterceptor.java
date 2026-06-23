package edu.jxut.sft.interceptor;

import edu.jxut.sft.entity.User;
import org.springframework.web.servlet.HandlerInterceptor;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;

public class LoginInterceptor implements HandlerInterceptor {

    /** 不需要登录的路径前缀 */
    private static final String[] EXCLUDE_PATHS = {
        "/sft/auth/",
        "/sft/dashboard/",
        "/druid/",
        "/css/",
        "/js/",
        "/img/"
    };

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response,
                             Object handler) throws Exception {
        String path = request.getRequestURI();
        // 放行排除路径
        for (String exclude : EXCLUDE_PATHS) {
            if (path.startsWith(exclude) || path.equals("/")) {
                return true;
            }
        }
        // 检查会话
        HttpSession session = request.getSession(false);
        if (session != null && session.getAttribute("loginUser") instanceof User) {
            return true;
        }
        // AJAX 请求返回 JSON
        if ("XMLHttpRequest".equals(request.getHeader("X-Requested-With"))) {
            response.setContentType("application/json;charset=UTF-8");
            response.getWriter().write("{\"code\":401,\"message\":\"未登录\",\"data\":null}");
            return false;
        }
        // 普通请求重定向到登录页
        response.sendRedirect(request.getContextPath() + "/login.html");
        return false;
    }
}
