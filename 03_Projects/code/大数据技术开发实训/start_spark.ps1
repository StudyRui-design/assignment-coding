$projectDir = "d:\Study\code\大数据技术开发实训"
Set-Location $projectDir
$m2 = "$env:USERPROFILE\.m2\repository"

Write-Host "=== Spark Microservice (port 9090) ===" -ForegroundColor Green

# Collect ALL jars from these key directories in Maven repo
$paths = @(
    "org/apache/spark", "org/eclipse/jetty", "org/scala-lang",
    "javax/servlet", "com/fasterxml/jackson", "com/google/guava",
    "io/netty", "com/esotericsoftware/kryo", "org/roaringbitmap",
    "org/apache/commons", "org/apache/hadoop", "org/apache/arrow",
    "org/apache/avro", "org/apache/parquet", "org/apache/orc",
    "org/apache/ivy", "org/apache/xbean", "org/apache/curator",
    "org/apache/zookeeper", "org/apache/logging", "org/xerial/snappy",
    "org/lz4", "com/github/luben", "org/fusesource", "org/slf4j",
    "org/objenesis", "org/json4s", "org/tukaani",
    "org/codehaus/janino", "org/codehaus/jackson",
    "com/clearspring/analytics", "com/thoughtworks/paranamer",
    "com/typesafe", "com/nimbusds", "io/dropwizard/metrics",
    "commons-io", "commons-cli", "commons-lang", "commons-codec",
    "commons-logging", "commons-collections", "commons-net",
    "commons-beanutils", "commons-pool", "commons-compress",
    "log4j", "com/sun/xml/bind", "org/glassfish/jaxb"
)

$jars = @()
foreach ($p in $paths) {
    $d = Join-Path $m2 $p
    if (Test-Path $d) {
        $j = Get-ChildItem -Path $d -Recurse -Filter "*.jar" -ErrorAction SilentlyContinue
        $jars += $j
    }
}
$jars = $jars | Sort-Object FullName -Unique

# Also add the existing spring boot deps
$bootLibs = Get-ChildItem "$projectDir\BOOT-INF\lib\*.jar" -ErrorAction SilentlyContinue

Write-Host "Maven repo jars: $($jars.Count), BOOT-INF jars: $($bootLibs.Count)" -ForegroundColor Cyan

# Build classpath
$cpParts = @("$projectDir\target\classes")
$cpParts += ($jars | ForEach-Object { $_.FullName })
if ($bootLibs) { $cpParts += ($bootLibs | ForEach-Object { $_.FullName }) }
$cp = $cpParts -join ";"

Write-Host "Starting SparkServer..."
$logFile = "$projectDir\spark_output2.log"
try {
    & java -cp $cp edu.jxut.sft.SparkServer 2>&1 | Tee-Object -FilePath $logFile
} catch {
    Write-Host "ERROR: $_" -ForegroundColor Red
}
Write-Host "Process ended." -ForegroundColor Yellow
Read-Host "Press Enter"
