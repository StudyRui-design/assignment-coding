/**
 * 用户信息自动填充 - 从 session 获取当前登录用户并显示在页面头部
 */
$(function() {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/sft/auth/session', true);
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4 && xhr.status === 200) {
            try {
                var data = JSON.parse(xhr.responseText);
                // AuthController 返回 {code:200, data:{realName,username,...}}
                var user = (data && data.data) || data || {};
                if (user && (user.realName || user.username)) {
                    var displayName = user.realName || user.username;
                    var showUser = document.getElementById('showUser');
                    if (showUser) showUser.textContent = ' ' + displayName + ' ';
                    var welcomeName = document.getElementById('welcomeName');
                    if (welcomeName) welcomeName.textContent = displayName;
                }
            } catch(e) {}
        }
    };
    xhr.send();
});
