import org.apache.spark.sql.SparkSession

/**
 * MovieLens 1M 数据集 SSQL 数据分析
 *
 * ==================== 数据源配置 ====================
 *
 * 支持三种运行模式，通过命令行参数或直接修改下方 DATA_ROOT 常量切换：
 *
 *   【模式1】本地文件（默认，无需 HDFS）
 *     将 ml-1m.zip 解压后的 users.dat / movies.dat / ratings.dat
 *     放到项目根目录下的 data/ml-1m/ 中，直接 Run 即可。
 *     数据集下载: https://files.grouplens.org/datasets/movielens/ml-1m.zip
 *
 *   【模式2】HDFS 集群
 *     scala DATA_ROOT="hdfs://192.168.88.131:8020/ml-1m"
 *     或直接修改下方 DATA_ROOT 为 HDFS 路径。
 *
 *   【模式3】任意自定义路径
 *     scala DATA_ROOT="/your/custom/path"
 *
 * ==================== MySQL 配置 ====================
 *
 *   默认写入 192.168.88.131:3306/movielens。
 *   如果 MySQL 不可达，将 DATA_TO_MYSQL 设为 false，程序只做控制台展示。
 *
 * ==================== 运行方式 ====================
 *
 *   IDEA 中直接右键 Run 'MovieAnalysis'（使用默认配置）
 *   或 spark-submit --class MovieAnalysis xxx.jar [DATA_ROOT] [MYSQL_HOST]
 */

object MovieAnalysis {

  // ============================================================
  // ==================== 核心配置（按需修改） ====================
  // ============================================================

  /** 数据根目录：支持本地路径 或 hdfs://host:port/path */
  private val DATA_ROOT: String = {
    // 优先级: 系统属性 > 硬编码默认值（本地 data 目录）
    // 运行时可通过 -DDATA_ROOT=hdfs://... 或 -DDATA_ROOT=/path/to/data 覆盖
    Option(System.getProperty("DATA_ROOT")).getOrElse("data/ml-1m")
  }

  /** 是否将结果写入 MySQL。false 时仅控制台展示，不写库。 */
  private val WRITE_TO_MYSQL: Boolean = {
    Option(System.getProperty("WRITE_TO_MYSQL"))
      .map(_.toBoolean)
      .getOrElse(true)
  }

  /** MySQL 主机地址 */
  private val MYSQL_HOST: String = {
    Option(System.getProperty("MYSQL_HOST")).getOrElse("192.168.88.131")
  }

  /** MySQL 端口 */
  private val MYSQL_PORT: String = {
    Option(System.getProperty("MYSQL_PORT")).getOrElse("3306")
  }

  /** MySQL 数据库 */
  private val MYSQL_DB: String = {
    Option(System.getProperty("MYSQL_DB")).getOrElse("movielens")
  }

  /** MySQL 用户 */
  private val MYSQL_USER: String = {
    Option(System.getProperty("MYSQL_USER")).getOrElse("root")
  }

  /** MySQL 密码 */
  private val MYSQL_PASSWORD: String = {
    Option(System.getProperty("MYSQL_PASSWORD")).getOrElse("123456")
  }

  // ============================================================
  // ==================== 主入口 =================================
  // ============================================================

  def main(args: Array[String]): Unit = {

    // ---------- 确定数据路径 ----------
    val dataRoot = if (args.length > 0) args(0) else DATA_ROOT
    val isHdfs = dataRoot.startsWith("hdfs://")

    println(
      s"""
         |╔══════════════════════════════════════════════════╗
         |║     MovieLens 1M SSQL 数据分析                  ║
         |╠══════════════════════════════════════════════════╣
         |║  数据源:   $dataRoot
         |║  MySQL:    ${if (WRITE_TO_MYSQL) s"$MYSQL_HOST:$MYSQL_PORT/$MYSQL_DB" else "(不写入)"}
         |╚══════════════════════════════════════════════════╝
         |""".stripMargin)

    // 构建文件完整路径
    def pathOf(file: String): String = {
      if (isHdfs) s"$dataRoot/$file"
      else {
        // 本地文件：使用绝对路径，避免 Spark 工作目录问题
        val absPath = new java.io.File(s"$dataRoot/$file").getAbsolutePath
        s"file:///$absPath".replace("\\", "/")
      }
    }

    val usersPath = pathOf("users.dat")
    val moviesPath = pathOf("movies.dat")
    val ratingsPath = pathOf("ratings.dat")

    // ---------- 验证本地文件是否存在 ----------
    if (!isHdfs) {
      for ((name, p) <- Seq(("users.dat", usersPath), ("movies.dat", moviesPath), ("ratings.dat", ratingsPath))) {
        val f = new java.io.File(new java.net.URI(p))
        if (!f.exists()) {
          System.err.println(
            s"""
               |╔══════════════════════════════════════════════════════════╗
               |║  ERROR: 找不到数据文件: $name
               |║  期望路径: ${f.getAbsolutePath}
               |║
               |║  请按以下步骤获取数据:
               |║  1. 下载: https://files.grouplens.org/datasets/movielens/ml-1m.zip
               |║  2. 解压 ml-1m.zip
               |║  3. 将 users.dat, movies.dat, ratings.dat 拷贝到:
               |║     ${new java.io.File(dataRoot).getAbsolutePath}/
               |║  4. 重新运行
               |║
               |║  或者使用 HDFS 路径:
               |║    -DDATA_ROOT=hdfs://192.168.88.131:8020/ml-1m
               |╚══════════════════════════════════════════════════════════╝
               |""".stripMargin)
          sys.exit(1)
        }
      }
      println("[OK] 所有本地数据文件验证通过\n")
    }

    // ==================== 1. 创建 SparkSession ====================
    val spark = SparkSession.builder()
      .appName("MovieLens1M_Analysis")
      .master("local[*]")
      .config("spark.sql.adaptive.enabled", "true")
      .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
      .getOrCreate()

    // 降低日志噪音（可选，取消注释以启用）
    // spark.sparkContext.setLogLevel("WARN")

    import spark.implicits._

    println("[INFO] 正在读取数据文件...")

    // ==================== 2. 读取数据文件 ====================
    // 2.1 用户数据  UserID :: Gender :: Age :: Occupation :: ZipCode
    val usersRaw = spark.sparkContext.textFile(usersPath)
    val usersDF = usersRaw.map { line =>
      val fields = line.split("::")
      (fields(0).toInt, fields(1), fields(2).toInt, fields(3).toInt, fields(4))
    }.toDF("UserID", "Gender", "Age", "Occupation", "ZipCode")

    // 2.2 电影数据  MovieID :: Title :: Genres
    val moviesRaw = spark.sparkContext.textFile(moviesPath)
    val moviesDF = moviesRaw.map { line =>
      val fields = line.split("::")
      (fields(0).toInt, fields(1), fields(2))
    }.toDF("MovieID", "Title", "Genres")

    // 2.3 评分数据  UserID :: MovieID :: Rating :: Timestamp
    val ratingsRaw = spark.sparkContext.textFile(ratingsPath)
    val ratingsDF = ratingsRaw.map { line =>
      val fields = line.split("::")
      (fields(0).toInt, fields(1).toInt, fields(2).toDouble, fields(3).toLong)
    }.toDF("UserID", "MovieID", "Rating", "Timestamp")

    // 缓存数据（多次使用）
    usersDF.cache()
    moviesDF.cache()
    ratingsDF.cache()

    // 打印数据概览
    println(s"[INFO] 数据加载完成:")
    println(s"  users:   ${usersDF.count()} 条")
    println(s"  movies:   ${moviesDF.count()} 条 (预览前 5 行)")
    moviesDF.show(5, truncate = false)
    println(s"  ratings: ${ratingsDF.count()} 条\n")

    // ==================== 3. 注册临时视图 ====================
    usersDF.createOrReplaceTempView("users")
    moviesDF.createOrReplaceTempView("movies")
    ratingsDF.createOrReplaceTempView("ratings")

    // ==================== 4. MySQL 连接配置 ====================
    val jdbcUrl = s"jdbc:mysql://$MYSQL_HOST:$MYSQL_PORT/$MYSQL_DB" +
      "?useSSL=false" +
      "&serverTimezone=UTC" +
      "&characterEncoding=UTF-8" +
      "&allowPublicKeyRetrieval=true"

    val connProps = new java.util.Properties()
    connProps.setProperty("user", MYSQL_USER)
    connProps.setProperty("password", MYSQL_PASSWORD)
    connProps.setProperty("driver", "com.mysql.cj.jdbc.Driver")

    // ==================== 5. 任务1: 各职业群体中最受欢迎的电影类型 Top3 ====================
    println("\n===== 任务1: 各职业群体中最受欢迎的电影类型 Top3 =====")

    // 说明：MovieLens 1M 中 Genres 字段以竖线 "|" 分隔多种类型，如 "Action|Adventure|Sci-Fi"
    // SQL 中 split 的第二个参数 '\\|' ——
    //   Scala 三引号字符串里 \\ 是字面量两个反斜杠
    //   → Spark SQL 解析 '\\|' 时 \\ 转为 \，得到字符串值 "\|"
    //   → split() 以此作为 Java 正则，\| 匹配字面量竖线 "|"

    val task1 = spark.sql(
      """
        |SELECT Occupation, Genre, Cnt, rk FROM (
        |  SELECT Occupation, Genre, Cnt,
        |         ROW_NUMBER() OVER (PARTITION BY Occupation ORDER BY Cnt DESC) AS rk
        |  FROM (
        |    SELECT u.Occupation, Genre, COUNT(*) AS Cnt
        |    FROM ratings r
        |    JOIN users u ON r.UserID = u.UserID
        |    JOIN movies m ON r.MovieID = m.MovieID
        |    LATERAL VIEW explode(split(m.Genres, '\\|')) tmp AS Genre
        |    GROUP BY u.Occupation, Genre
        |  ) t
        |) t2
        |WHERE rk <= 3
        |ORDER BY Occupation, rk
      """.stripMargin)

    task1.show(60, truncate = false)

    if (WRITE_TO_MYSQL) {
      println("[INFO] 正在将任务1结果写入 MySQL: task1_occ_genre_top3 ...")
      task1
        .coalesce(1) // 小结果集合并为 1 个分区
        .write
        .mode("overwrite")
        .jdbc(jdbcUrl, "task1_occ_genre_top3", connProps)
      println("[OK]  任务1 写入完成")
    }

    // ==================== 6. 任务2: 25-34岁男性用户最爱的3种电影类型 ====================
    println("\n===== 任务2: 25-34岁男性用户最爱的3种电影类型 =====")

    // 说明：MovieLens 1M 中 Age 是年龄段代码（1=Under 18, 18=18-24, 25=25-34, ...）
    // Age BETWEEN 25 AND 34 精确命中 25-34 岁群体

    val task2 = spark.sql(
      """
        |SELECT Genre, COUNT(*) AS Cnt
        |FROM ratings r
        |JOIN users u ON r.UserID = u.UserID
        |JOIN movies m ON r.MovieID = m.MovieID
        |LATERAL VIEW explode(split(m.Genres, '\\|')) tmp AS Genre
        |WHERE u.Gender = 'M' AND u.Age BETWEEN 25 AND 34
        |GROUP BY Genre
        |ORDER BY Cnt DESC
        |LIMIT 3
      """.stripMargin)

    task2.show(truncate = false)

    if (WRITE_TO_MYSQL) {
      println("[INFO] 正在将任务2结果写入 MySQL: task2_male_25_34_top3_genre ...")
      task2
        .coalesce(1)
        .write
        .mode("overwrite")
        .jdbc(jdbcUrl, "task2_male_25_34_top3_genre", connProps)
      println("[OK]  任务2 写入完成")
    }

    // ==================== 7. 任务3: 1990年后女性评分占比 > 60% 的浪漫爱情片 Top10 ====================
    println("\n===== 任务3: 1990年后女性评分占比 > 60% 的浪漫爱情片 Top10 =====")

    // 说明：regexp_extract 从 Title 格式 "Movie Name (1995)" 中提取年份
    //   Scala 三引号字符串中 '\\((\\d{4})\\)' →
    //   Spark SQL 解析为字符串 "\((\d{4})\)" →
    //   Java regex: \( 匹配字面量 (，(\d{4}) 捕获 4 位年份，\) 匹配字面量 )

    val task3 = spark.sql(
      """
        |SELECT
        |  m.MovieID,
        |  m.Title,
        |  m.Genres,
        |  COUNT(*) AS TotalRatingCount,
        |  SUM(CASE WHEN u.Gender = 'F' THEN 1 ELSE 0 END) AS FemaleRatingCount,
        |  ROUND(AVG(r.Rating), 2) AS AvgRating,
        |  ROUND(SUM(CASE WHEN u.Gender = 'F' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS FemaleRatio
        |FROM ratings r
        |JOIN users u ON r.UserID = u.UserID
        |JOIN movies m ON r.MovieID = m.MovieID
        |WHERE m.Genres LIKE '%Romance%'
        |  AND CAST(regexp_extract(m.Title, '\\((\\d{4})\\)', 1) AS INT) >= 1990
        |GROUP BY m.MovieID, m.Title, m.Genres
        |HAVING FemaleRatio > 60
        |ORDER BY FemaleRatio DESC, AvgRating DESC
        |LIMIT 10
      """.stripMargin)

    task3.show(10, truncate = false)

    if (WRITE_TO_MYSQL) {
      println("[INFO] 正在将任务3结果写入 MySQL: task3_romance_female_top10 ...")
      task3
        .coalesce(1)
        .write
        .mode("overwrite")
        .jdbc(jdbcUrl, "task3_romance_female_top10", connProps)
      println("[OK]  任务3 写入完成")
    }

    // ==================== 8. 完成 ====================
    println("\n===== 所有分析任务完成! =====")
    if (WRITE_TO_MYSQL) {
      println(s"结果已写入 MySQL: $MYSQL_HOST:$MYSQL_PORT/$MYSQL_DB")
    }
    println()

    spark.stop()
  }
}
