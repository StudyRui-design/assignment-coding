@echo off
set JAVA_HOME=D:\Dev\Java\jdk1.8.0_121
set BASE=D:\Study\IELTS Practice Project\sft-springboot
set M2=C:\Users\26291\.m2\repository

set CP=%BASE%\target\classes

rem Spring Boot core
set CP=%CP%;%M2%/org/springframework/boot/spring-boot/2.7.18/spring-boot-2.7.18.jar
set CP=%CP%;%M2%/org/springframework/boot/spring-boot-autoconfigure/2.7.18/spring-boot-autoconfigure-2.7.18.jar

rem Logging
set CP=%CP%;%M2%/ch/qos/logback/logback-classic/1.2.12/logback-classic-1.2.12.jar
set CP=%CP%;%M2%/ch/qos/logback/logback-core/1.2.12/logback-core-1.2.12.jar
set CP=%CP%;%M2%/org/apache/logging/log4j/log4j-to-slf4j/2.17.2/log4j-to-slf4j-2.17.2.jar
set CP=%CP%;%M2%/org/apache/logging/log4j/log4j-api/2.17.2/log4j-api-2.17.2.jar
set CP=%CP%;%M2%/org/slf4j/jul-to-slf4j/1.7.36/jul-to-slf4j-1.7.36.jar
set CP=%CP%;%M2%/org/slf4j/slf4j-api/1.7.36/slf4j-api-1.7.36.jar

rem Jakarta
set CP=%CP%;%M2%/jakarta/annotation/jakarta.annotation-api/1.3.5/jakarta.annotation-api-1.3.5.jar

rem Spring Framework
set CP=%CP%;%M2%/org/springframework/spring-core/5.3.31/spring-core-5.3.31.jar
set CP=%CP%;%M2%/org/springframework/spring-jcl/5.3.31/spring-jcl-5.3.31.jar
set CP=%CP%;%M2%/org/springframework/spring-beans/5.3.31/spring-beans-5.3.31.jar
set CP=%CP%;%M2%/org/springframework/spring-context/5.3.31/spring-context-5.3.31.jar
set CP=%CP%;%M2%/org/springframework/spring-expression/5.3.31/spring-expression-5.3.31.jar
set CP=%CP%;%M2%/org/springframework/spring-web/5.3.31/spring-web-5.3.31.jar
set CP=%CP%;%M2%/org/springframework/spring-webmvc/5.3.31/spring-webmvc-5.3.31.jar
set CP=%CP%;%M2%/org/springframework/spring-jdbc/5.3.31/spring-jdbc-5.3.31.jar
set CP=%CP%;%M2%/org/springframework/spring-tx/5.3.31/spring-tx-5.3.31.jar
set CP=%CP%;%M2%/org/springframework/spring-aop/5.3.31/spring-aop-5.3.31.jar

rem YAML
set CP=%CP%;%M2%/org/yaml/snakeyaml/1.30/snakeyaml-1.30.jar

rem Jackson
set CP=%CP%;%M2%/com/fasterxml/jackson/core/jackson-databind/2.13.5/jackson-databind-2.13.5.jar
set CP=%CP%;%M2%/com/fasterxml/jackson/core/jackson-annotations/2.13.5/jackson-annotations-2.13.5.jar
set CP=%CP%;%M2%/com/fasterxml/jackson/core/jackson-core/2.13.5/jackson-core-2.13.5.jar
set CP=%CP%;%M2%/com/fasterxml/jackson/datatype/jackson-datatype-jdk8/2.13.5/jackson-datatype-jdk8-2.13.5.jar
set CP=%CP%;%M2%/com/fasterxml/jackson/datatype/jackson-datatype-jsr310/2.13.5/jackson-datatype-jsr310-2.13.5.jar
set CP=%CP%;%M2%/com/fasterxml/jackson/module/jackson-module-parameter-names/2.13.5/jackson-module-parameter-names-2.13.5.jar

rem Tomcat
set CP=%CP%;%M2%/org/apache/tomcat/embed/tomcat-embed-core/9.0.83/tomcat-embed-core-9.0.83.jar
set CP=%CP%;%M2%/org/apache/tomcat/embed/tomcat-embed-el/9.0.83/tomcat-embed-el-9.0.83.jar
set CP=%CP%;%M2%/org/apache/tomcat/embed/tomcat-embed-websocket/9.0.83/tomcat-embed-websocket-9.0.83.jar

rem HikariCP
set CP=%CP%;%M2%/com/zaxxer/HikariCP/4.0.3/HikariCP-4.0.3.jar

rem Security
set CP=%CP%;%M2%/org/springframework/security/spring-security-config/5.7.11/spring-security-config-5.7.11.jar
set CP=%CP%;%M2%/org/springframework/security/spring-security-core/5.7.11/spring-security-core-5.7.11.jar
set CP=%CP%;%M2%/org/springframework/security/spring-security-crypto/5.7.11/spring-security-crypto-5.7.11.jar
set CP=%CP%;%M2%/org/springframework/security/spring-security-web/5.7.11/spring-security-web-5.7.11.jar

rem MySQL
set CP=%CP%;%M2%/mysql/mysql-connector-java/8.0.30/mysql-connector-java-8.0.30.jar
set CP=%CP%;%M2%/com/google/protobuf/protobuf-java/3.19.4/protobuf-java-3.19.4.jar

rem FastJSON
set CP=%CP%;%M2%/com/alibaba/fastjson/1.2.83/fastjson-1.2.83.jar

echo Starting Spring Boot...
%JAVA_HOME%\bin\java -Xverify:none -XX:TieredStopAtLevel=1 -cp "%CP%" edu.jxut.sft.SftApplication
pause
