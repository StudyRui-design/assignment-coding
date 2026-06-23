package edu.jxut.sft.untils;

import java.sql.Connection;

// 专门测试DbUtil能否获取数据库连接的类
public class DbUtilTest {
    public static void main(String[] args) {
        // 调用DbUtil的getConnection()方法，尝试获取连接
        Connection conn = DbUtil.getConnection();

        // 根据连接是否为null，判断是否成功
        if (conn != null) {
            System.out.println("✅ DbUtil连接数据库成功！");
            // 若成功，记得关闭连接（避免资源泄漏）
            try {
                conn.close();
                System.out.println("✅ 连接已关闭");
            } catch (Exception e) {
                e.printStackTrace();
            }
        } else {
            System.out.println("❌ DbUtil连接数据库失败！");
            // 失败时，控制台会打印DbUtil中e.printStackTrace()的异常信息，根据异常排查
        }
    }
}