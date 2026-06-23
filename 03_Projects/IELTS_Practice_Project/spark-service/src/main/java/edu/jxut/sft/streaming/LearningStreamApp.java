package edu.jxut.sft.streaming;

import edu.jxut.sft.config.AppConfig;
import edu.jxut.sft.config.SparkConfig;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SparkSession;
import org.apache.spark.sql.streaming.StreamingQuery;
import org.apache.spark.sql.streaming.Trigger;

import java.util.concurrent.atomic.AtomicBoolean;

/**
 * Spark Structured Streaming — real-time learning behavior monitor.
 *
 * Reads study records from a "study_events" table (or file sink)
 * and computes per-minute stats.
 *
 * Usage:
 *   1. An external producer writes new study rows into a table/file.
 *   2. This streaming query reads them in micro-batches.
 *   3. Aggregated results are written to "study_analytics" table.
 *
 * NOTE: Requires Spark to read from a streaming source.
 * In development mode, use rate() source for demo.
 */
public class LearningStreamApp {

    private static final AtomicBoolean running = new AtomicBoolean(false);

    /**
     * Start the streaming query in a background thread.
     */
    public static synchronized void start() {
        if (running.get()) {
            System.out.println("⚠ Streaming is already running.");
            return;
        }

        Thread t = new Thread(() -> {
            try {
                runStream();
            } catch (Exception e) {
                System.err.println("❌ Streaming stopped: " + e.getMessage());
                e.printStackTrace();
            }
        }, "streaming-worker");
        t.setDaemon(true);
        t.start();
        running.set(true);
        System.out.println("✓ Real-time streaming monitor started");
    }

    private static void runStream() throws Exception {
        SparkSession spark = SparkConfig.getSparkSession();

        // In production, replace with:
        //   spark.readStream()
        //       .format("kafka")
        //       .option("kafka.bootstrap.servers", "localhost:9092")
        //       .option("subscribe", "study-events")
        //       .load()
        //
        // For now, use a file-based streaming source for demo:
        // Watch a directory for new CSV/JSON files.

        // ===== Demo: rate-based synthetic stream =====
        Dataset<Row> stream = spark.readStream()
                .format("rate")
                .option("rowsPerSecond", 1)
                .option("numPartitions", 1)
                .load();

        // Simulate aggregating study metrics per minute
        Dataset<Row> agg = stream
                .withWatermark("timestamp", "1 minute")
                .groupBy(
                        org.apache.spark.sql.functions.window(
                                stream.col("timestamp"), "1 minute"))
                .count()
                .withColumnRenamed("count", "eventCount");

        StreamingQuery query = agg.writeStream()
                .outputMode("append")
                .trigger(Trigger.ProcessingTime("30 seconds"))
                .format("console")
                .option("truncate", false)
                .start();

        System.out.println("✓ Streaming query: " + query.name());
        System.out.println("  → output to console (30-sec micro-batch)");
        System.out.println("  → To use real data, replace format(\"rate\") with");
        System.out.println("    format(\"kafka\") or file source in production.");
    }

    public static boolean isRunning() {
        return running.get();
    }
}
