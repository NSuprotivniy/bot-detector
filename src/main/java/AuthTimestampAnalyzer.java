import org.apache.spark.mllib.stat.Statistics;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SparkSession;
import org.apache.spark.sql.types.DataTypes;
import static org.apache.spark.sql.functions.*;

import java.io.IOException;

public class AuthTimestampAnalyzer {

    public static void main(String[] args) {
        SparkSession spark = SparkSession
                .builder()
                .appName("Java Spark SQL basic example")
                .master("local[4]")
                .getOrCreate();

        Dataset<Row> df = spark.read().option("header", "true").csv("../bots_logins.csv");
        df.printSchema();

        df = df.withColumn("IP", col("IP").cast(DataTypes.IntegerType))
                .withColumn("TIMESTAMP", col("TIMESTAMP").cast(DataTypes.LongType));

        spark.sqlContext().udf().register("intToIp",
                (Integer ip) -> Utils.IPConverter.intToIp(ip),
                DataTypes.StringType);

        Dataset<Row> IPSeries = df.select(col("IP"), col("TIMESTAMP"));
        IPSeries = IPSeries.withColumn("IP", callUDF("intToIp", col("IP")));
        IPSeries.show();

        Dataset<Row> IPSimpleStat = IPSeries.groupBy("IP").agg(
                mean("TIMESTAMP").cast(DataTypes.LongType).alias("MEAN"),
                variance("TIMESTAMP").alias("variance"),
                max("TIMESTAMP").alias("MAX"),
                min("TIMESTAMP").alias("MIN")

        );

        IPSimpleStat.show();

        // https://spark.apache.org/docs/latest/mllib-statistics.html
    }
}
