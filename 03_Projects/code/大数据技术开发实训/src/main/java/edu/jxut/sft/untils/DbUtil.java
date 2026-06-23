package edu.jxut.sft.untils;

import java.io.IOException;
import java.io.InputStream;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.Properties;

/**
 * 数据库工具类 - 支持配置文件读取
 * @author guorf
 */
public class DbUtil {

    private static String driver;
    private static String url;
    private static String username;
    private static String password;

    static {
        try {
            // 从配置文件加载数据库连接信息，避免硬编码
            Properties props = new Properties();
            InputStream in = DbUtil.class.getClassLoader()
                    .getResourceAsStream("db.properties");
            if (in != null) {
                props.load(in);
                driver = props.getProperty("jdbc.driver", "com.mysql.cj.jdbc.Driver");
                url = props.getProperty("jdbc.url",
                        "jdbc:mysql://127.0.0.1:3306/test?useUnicode=true&characterEncoding=utf-8&useSSL=false&serverTimezone=Asia/Shanghai&allowPublicKeyRetrieval=true");
                username = props.getProperty("jdbc.username", "root");
                password = props.getProperty("jdbc.password", "123456");
                in.close();
            } else {
                // 配置文件不存在时使用默认值（仅开发环境）
                driver = "com.mysql.cj.jdbc.Driver";
                url = "jdbc:mysql://127.0.0.1:3306/test?useUnicode=true&characterEncoding=utf-8&useSSL=false&serverTimezone=Asia/Shanghai&allowPublicKeyRetrieval=true";
                username = "root";
                password = "123456";
            }
            Class.forName(driver);
        } catch (Exception e) {
            e.printStackTrace();
            throw new RuntimeException("数据库驱动加载失败", e);
        }
    }

    public static Connection getConnection() {
        try {
            return DriverManager.getConnection(url, username, password);
        } catch (SQLException e) {
            throw new RuntimeException("数据库连接失败: " + e.getMessage(), e);
        }
    }

    public static void closeAll(Connection conn, Statement stmt, ResultSet rs) {
        try {
            if (rs != null) {
                rs.close();
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
        try {
            if (stmt != null) {
                stmt.close();
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
        try {
            if (conn != null) {
                conn.close();
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }
}
