# -*- coding: utf-8 -*-
"""Spark 电影数据分析 — 主入口

用法：
  spark-submit main.py [--skip-mysql] [--skip-hdfs]

流程：
  1. 创建 SparkSession
  2. 加载 MovieLens 1M 数据 → 注册 SQL 临时视图
  3. 执行全部 Spark SQL 分析查询
  4. 控制台打印结果
  5. 写入 MySQL
  6. 写入 HDFS
"""

import sys
import time
from data_loader import create_spark_session, register_all_tables
from analysis_queries import run_all_analyses, show_all
from write_mysql import write_all_to_mysql
from write_hdfs import write_all_to_hdfs


def main():
    skip_mysql = "--skip-mysql" in sys.argv
    skip_hdfs = "--skip-hdfs" in sys.argv

    print("=" * 60)
    print("  Spark SQL 电影数据分析 — MovieLens 1M")
    print("=" * 60)

    # ── 1. 创建 SparkSession ──
    t0 = time.time()
    spark = create_spark_session()
    print(f"\n✓ SparkSession 创建成功 (appName: {spark.sparkContext.appName})")

    # ── 2. 加载数据 ──
    register_all_tables(spark)
    print("✓ 数据加载完成：movies / ratings / users 三表已注册为 SQL 视图")

    # ── 3. 执行分析 ──
    results = run_all_analyses(spark)

    # ── 4. 控制台展示 ──
    show_all(results, n=15)

    # ── 5. 写入 MySQL ──
    if not skip_mysql:
        write_all_to_mysql(results)
    else:
        print("\n  ⏭ 跳过 MySQL 写入 (--skip-mysql)")

    # ── 6. 写入 HDFS ──
    if not skip_hdfs:
        write_all_to_hdfs(results)
    else:
        print("\n  ⏭ 跳过 HDFS 写入 (--skip-hdfs)")

    elapsed = time.time() - t0
    print(f"\n{'=' * 60}")
    print(f"  全流程完成，耗时 {elapsed:.1f} 秒")
    print(f"{'=' * 60}")

    spark.stop()


if __name__ == "__main__":
    main()
