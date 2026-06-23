# 邓睿的大数据应用课件管理系统 - 部署指南

## 项目概述

基于 Spring Boot 2.7 + MySQL 的课件管理系统，支持科目管理、课件管理、用户管理、密码修改等功能。

## 技术栈

| 技术 | 版本 |
|------|------|
| Java | 1.8+ |
| Spring Boot | 2.7.18 |
| MySQL | 8.0 |
| 前端 | HTML + CSS + jQuery + AJAX |
| 连接池 | HikariCP（Spring Boot默认） |
| 密码加密 | SHA-256 + 随机盐值 |

## 快速部署

### 方式一：Docker Compose 一键部署（推荐）

```bash
# 1. 进入项目目录
cd 大数据技术开发实训

# 2. 启动服务（自动构建并启动 MySQL + 应用）
docker-compose up -d

# 3. 查看日志
docker-compose logs -f app

# 4. 访问系统
# http://localhost:8080/sft/login.html
```

### 方式二：手动部署

#### 1. 准备 MySQL 数据库

```bash
# 创建数据库并初始化表结构
mysql -u root -p < init.sql
```

#### 2. 修改数据库配置

编辑 `src/main/resources/application.yml`，修改数据库连接信息：
```yaml
spring:
  datasource:
    url: jdbc:mysql://127.0.0.1:3306/test?...
    username: root
    password: your_password
```

#### 3. 编译打包

```bash
mvn clean package -DskipTests
```

#### 4. 运行

```bash
java -jar target/sft.jar
```

#### 5. 访问系统

打开浏览器访问：`http://localhost:8080/sft/login.html`

## 项目结构

```
├── pom.xml                    # Maven 配置（Spring Boot）
├── Dockerfile                 # Docker 镜像构建文件
├── docker-compose.yml         # Docker Compose 编排文件
├── init.sql                   # 数据库初始化脚本
├── src/main/java/edu/jxut/sft/
│   ├── SftApplication.java   # Spring Boot 启动类
│   ├── controller/            # Controller 层
│   │   ├── UserController.java         # 登录/注册
│   │   ├── PasswordController.java     # 密码修改
│   │   ├── SubjectController.java      # 科目管理
│   │   └── StudyController.java        # 课件管理
│   ├── Service/               # Service 层
│   │   ├── SubjectService.java / SubjectServiceImpl.java
│   │   └── StudyService.java / StudyServiceImpl.java
│   ├── dao/                   # DAO 层
│   │   ├── SubjectDao.java / SubjectDaoImpl.java
│   │   └── StudyDao.java / StudyDaoImpl.java
│   ├── pojo/                  # 实体类
│   │   ├── Subject.java
│   │   └── Study.java
│   └── untils/                # 工具类
│       ├── DbUtil.java        # 数据库连接工具
│       ├── PasswordUtil.java  # 密码加密工具
│       ├── PageUtil.java      # 分页工具
│       ├── StringUtil.java    # 字符串工具
│       └── DateUtil.java      # 日期工具
├── src/main/resources/
│   ├── application.yml        # Spring Boot 配置
│   └── db.properties          # 数据库配置（备用）
└── src/main/webapp/           # 前端页面
    ├── login.html / register.html
    ├── index.html
    ├── subjectList.html / subjectAdd.html / subjectUpdate.html
    ├── studyList.html / studyAdd.html / studyUpdate.html / studyView.html
    ├── userList.html / userAdd.html / userUpdate.html / userView.html
    └── password.html
```

## 优化内容总结

### 1. 安全优化
- ✅ 密码使用 SHA-256 + 随机盐值加密存储（`PasswordUtil.java`）
- ✅ 登录验证不再明文对比密码，支持新旧密码格式兼容
- ✅ 数据库配置从硬编码改为外部配置文件
- ✅ 添加参数空值校验和异常处理

### 2. 架构升级
- ✅ 从传统 Servlet 升级为 Spring Boot 2.7
- ✅ 引入 HikariCP 数据库连接池
- ✅ 打包方式从 WAR 改为可执行 JAR（内嵌 Tomcat）
- ✅ Java 版本从 7 升级到 8

### 3. 功能补全
- ✅ 课件管理完整 CRUD（后端 + AJAX 前端）
- ✅ 密码修改功能（含旧密码验证）
- ✅ 用户登录会话管理
- ✅ 科目管理添加失败反馈

### 4. 代码质量
- ✅ 清理重复的 import 语句
- ✅ 移除调试用的 System.out.println
- ✅ 统一异常处理
- ✅ 修复资源泄漏（try-with-resources）

### 5. 部署支持
- ✅ Dockerfile（多阶段构建）
- ✅ docker-compose.yml（MySQL + 应用一键部署）
- ✅ 数据库初始化脚本（init.sql）
