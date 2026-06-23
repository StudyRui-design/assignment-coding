package edu.jxut.sft.untils;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.security.SecureRandom;
import java.util.Base64;

/**
 * 密码加密工具类 - 使用 SHA-256 + 随机盐值
 */
public class PasswordUtil {

    private static final int SALT_LENGTH = 16;

    /**
     * 加密密码，生成 "salt:hash" 格式的密文
     */
    public static String encrypt(String plainPassword) {
        byte[] salt = generateSalt();
        String hash = sha256(plainPassword, salt);
        return Base64.getEncoder().encodeToString(salt) + ":" + hash;
    }

    /**
     * 验证密码
     * @param plainPassword 明文密码
     * @param storedPassword 数据库中存储的密文（支持 "salt:hash" 格式和旧版明文）
     */
    public static boolean verify(String plainPassword, String storedPassword) {
        if (storedPassword == null || plainPassword == null) {
            return false;
        }

        // 兼容旧版明文密码（不含 ":" 分隔符的视为明文）
        if (!storedPassword.contains(":")) {
            return storedPassword.equals(plainPassword);
        }

        // 新版加密密码验证
        String[] parts = storedPassword.split(":", 2);
        if (parts.length != 2) {
            return false;
        }
        try {
            byte[] salt = Base64.getDecoder().decode(parts[0]);
            String hash = sha256(plainPassword, salt);
            return hash.equals(parts[1]);
        } catch (IllegalArgumentException e) {
            // Base64 解码失败，密码格式无效
            return false;
        }
    }

    private static byte[] generateSalt() {
        SecureRandom random = new SecureRandom();
        byte[] salt = new byte[SALT_LENGTH];
        random.nextBytes(salt);
        return salt;
    }

    private static String sha256(String password, byte[] salt) {
        try {
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            md.update(salt);
            byte[] hashed = md.digest(password.getBytes(StandardCharsets.UTF_8));
            return bytesToHex(hashed);
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException("SHA-256算法不可用", e);
        }
    }

    private static String bytesToHex(byte[] bytes) {
        StringBuilder sb = new StringBuilder();
        for (byte b : bytes) {
            sb.append(String.format("%02x", b));
        }
        return sb.toString();
    }
}
