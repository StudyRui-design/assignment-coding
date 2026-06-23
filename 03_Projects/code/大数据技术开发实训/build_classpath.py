#!/usr/bin/env python3
"""
从 Maven 本地仓库递归收集依赖 jar，构建完整 classpath 并启动 SparkServer。
"""
import os
import re
import sys
import xml.etree.ElementTree as ET
import subprocess

MAVEN_REPO = os.path.expanduser("~/.m2/repository")
PROJECT_DIR = r"d:\Study\code\大数据技术开发实训"

# 直接依赖列表 (groupId, artifactId, version)
DIRECT_DEPS = [
    ("org.springframework.boot", "spring-boot-starter-web", "2.7.18"),
    ("org.springframework.boot", "spring-boot-starter-jdbc", "2.7.18"),
    ("org.springframework.boot", "spring-boot-starter-thymeleaf", "2.7.18"),
    ("mysql", "mysql-connector-java", "8.0.30"),
    ("com.alibaba.fastjson2", "fastjson2", "2.0.53"),
    ("org.apache.spark", "spark-core_2.12", "3.3.4"),
    ("org.apache.spark", "spark-sql_2.12", "3.3.4"),
    ("org.eclipse.jetty", "jetty-server", "9.4.53.v20231009"),
    ("org.eclipse.jetty", "jetty-servlet", "9.4.53.v20231009"),
    ("org.eclipse.jetty", "jetty-util", "9.4.53.v20231009"),
    ("org.eclipse.jetty", "jetty-http", "9.4.53.v20231009"),
    ("org.eclipse.jetty", "jetty-io", "9.4.53.v20231009"),
    ("javax.servlet", "javax.servlet-api", "3.1.0"),
    ("org.scala-lang", "scala-library", "2.12.15"),
    ("org.slf4j", "slf4j-api", "1.7.36"),
    ("ch.qos.logback", "logback-classic", "1.2.12"),
    ("ch.qos.logback", "logback-core", "1.2.12"),
    ("org.slf4j", "jcl-over-slf4j", "1.7.36"),
    ("org.slf4j", "jul-to-slf4j", "1.7.36"),
    ("org.slf4j", "log4j-over-slf4j", "1.7.36"),
    ("io.dropwizard.metrics", "metrics-core", "4.2.19"),
    ("io.dropwizard.metrics", "metrics-jmx", "4.2.19"),
    ("io.dropwizard.metrics", "metrics-jvm", "4.2.19"),
    ("io.dropwizard.metrics", "metrics-graphite", "4.2.19"),
    ("io.dropwizard.metrics", "metrics-json", "4.2.19"),
    ("io.netty", "netty-all", "4.1.96.Final"),
    ("com.fasterxml.jackson.module", "jackson-module-scala_2.12", "2.13.5"),
]

# NS mapping for Maven POM
NS = {'m': 'http://maven.apache.org/POM/4.0.0'}

def resolve_jar(groupId, artifactId, version):
    """返回 jar 的绝对路径"""
    path = os.path.join(
        MAVEN_REPO,
        groupId.replace('.', os.sep),
        artifactId,
        version,
        f"{artifactId}-{version}.jar"
    )
    if os.path.exists(path):
        return path
    print(f"  [WARN] JAR not found: {path}")
    return None

def resolve_pom(groupId, artifactId, version):
    """返回 POM 的绝对路径"""
    path = os.path.join(
        MAVEN_REPO,
        groupId.replace('.', os.sep),
        artifactId,
        version,
        f"{artifactId}-{version}.pom"
    )
    if os.path.exists(path):
        return path
    return None

def parse_deps_from_pom(pom_path):
    """从 POM 文件中解析依赖，支持属性替换"""
    deps = []
    try:
        tree = ET.parse(pom_path)
        root = tree.getroot()
        
        # 收集 POM 属性 (properties)
        props = {}
        props_elem = root.find('m:properties', NS)
        if props_elem is not None:
            for child in props_elem:
                tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                props[tag] = child.text.strip() if child.text else ''
        
        # 添加内置属性
        pom_group = root.find('m:groupId', NS)
        pom_artifact = root.find('m:artifactId', NS)
        pom_version = root.find('m:version', NS)
        if pom_group is not None:
            props['project.groupId'] = pom_group.text.strip()
        if pom_artifact is not None:
            props['project.artifactId'] = pom_artifact.text.strip()
        if pom_version is not None:
            props['project.version'] = pom_version.text.strip()
        
        # 处理 parent
        parent = root.find('m:parent', NS)
        if parent is not None:
            pg = parent.find('m:groupId', NS)
            pa = parent.find('m:artifactId', NS)
            pv = parent.find('m:version', NS)
            if pg is not None and pa is not None and pv is not None:
                deps.append((pg.text.strip(), pa.text.strip(), pv.text.strip()))
        
        def resolve(value):
            """Resolve ${...} placeholders using POM properties"""
            if value is None:
                return None
            text = value.text.strip() if value.text else ''
            # Replace ${...} with known properties
            import re
            def replacer(m):
                key = m.group(1)
                return props.get(key, m.group(0))
            return re.sub(r'\$\{([^}]+)\}', replacer, text)
        
        # 处理 dependencies
        deps_node = root.find('m:dependencies', NS)
        if deps_node is not None:
            for dep in deps_node.findall('m:dependency', NS):
                g = dep.find('m:groupId', NS)
                a = dep.find('m:artifactId', NS)
                v = dep.find('m:version', NS)
                scope = dep.find('m:scope', NS)
                
                if scope is not None and scope.text.strip() == 'test':
                    continue
                
                if g is not None and a is not None:
                    ga = resolve(g)
                    aa = resolve(a)
                    
                    if v is not None and v.text:
                        va = resolve(v)
                        if not va or '${' in va:
                            va = resolve_version_from_parent(pom_path, ga, aa)
                            if va is None:
                                print(f"  [SKIP] Unresolved version for {ga}:{aa} (raw: {v.text.strip()})")
                                continue
                    else:
                        va = resolve_version_from_parent(pom_path, ga, aa)
                        if va is None:
                            print(f"  [SKIP] No version for {ga}:{aa}")
                            continue
                    
                    deps.append((ga, aa, va))
    except Exception as e:
        print(f"  [ERROR] Failed to parse {pom_path}: {e}")
    return deps

def resolve_version_from_parent(pom_path, groupId, artifactId):
    """从父 POM 的 dependencyManagement 解析版本"""
    try:
        tree = ET.parse(pom_path)
        root = tree.getroot()
        parent = root.find('m:parent', NS)
        if parent is not None:
            pg = parent.find('m:groupId', NS)
            pa = parent.find('m:artifactId', NS)
            pv = parent.find('m:version', NS)
            if pg is not None and pa is not None and pv is not None:
                parent_pom = resolve_pom(pg.text.strip(), pa.text.strip(), pv.text.strip())
                if parent_pom:
                    tree2 = ET.parse(parent_pom)
                    root2 = tree2.getroot()
                    dm = root2.find('m:dependencyManagement/m:dependencies', NS)
                    if dm is not None:
                        for dep in dm.findall('m:dependency', NS):
                            g = dep.find('m:groupId', NS)
                            a = dep.find('m:artifactId', NS)
                            v = dep.find('m:version', NS)
                            if (g is not None and a is not None and v is not None and
                                g.text.strip() == groupId and a.text.strip() == artifactId):
                                return v.text.strip()
    except:
        pass
    return None

def collect_all_jars(direct_deps):
    """递归收集所有依赖 jar 路径"""
    visited = set()
    to_process = list(direct_deps)
    jars = []
    
    while to_process:
        ga, aa, va = to_process.pop(0)
        key = f"{ga}:{aa}:{va}"
        if key in visited:
            continue
        visited.add(key)
        
        jar_path = resolve_jar(ga, aa, va)
        if jar_path:
            jars.append(jar_path)
            print(f"  [OK] {key}")
        else:
            # 可能是 BOM (bill of materials) 类型，只解析 POM
            print(f"  [POM only] {key}")
        
        pom_path = resolve_pom(ga, aa, va)
        if pom_path:
            transitive = parse_deps_from_pom(pom_path)
            for t in transitive:
                if f"{t[0]}:{t[1]}:{t[2]}" not in visited:
                    to_process.append(t)
    
    return jars

def main():
    print("=" * 60)
    print("Collecting all Maven dependencies...")
    print("=" * 60)
    
    all_jars = collect_all_jars(DIRECT_DEPS)
    
    # 添加项目编译输出
    classes_dir = os.path.join(PROJECT_DIR, "target", "classes")
    if os.path.exists(classes_dir):
        all_jars.insert(0, classes_dir)
        print(f"  [ADDED] Classes: {classes_dir}")
    
    # 去重
    all_jars = list(dict.fromkeys(all_jars))
    
    # 构建 classpath
    cp = ";".join(all_jars)
    
    print(f"\n{'=' * 60}")
    print(f"Total jars: {len(all_jars)}")
    print(f"Classpath length: {len(cp)} chars")
    print(f"{'=' * 60}")
    
    # 保存 classpath 到文件供 bat 使用
    cp_file = os.path.join(PROJECT_DIR, "spark_cp.txt")
    with open(cp_file, "w", encoding="utf-8") as f:
        for jar in all_jars:
            f.write(jar + "\n")
    print(f"Classpath saved to: {cp_file}")
    
    # 启动 SparkServer - 输出到日志文件
    log_file = os.path.join(PROJECT_DIR, "spark_run.log")
    print(f"\nStarting SparkServer on port 9090...")
    print(f"Logs -> {log_file}")
    
    cmd = ["java", "-cp", cp, "edu.jxut.sft.SparkServer"]
    
    with open(log_file, "w", encoding="utf-8") as log:
        try:
            proc = subprocess.Popen(
                cmd,
                cwd=PROJECT_DIR,
                stdout=log,
                stderr=subprocess.STDOUT
            )
            print(f"Process started with PID: {proc.pid}")
        except Exception as e:
            print(f"Failed to start: {e}")

if __name__ == "__main__":
    main()
