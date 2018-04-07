import Helpers.GetVMSpark;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SparkSession;
import org.apache.spark.sql.types.DataTypes;
import static org.apache.spark.sql.functions.*;


public class AuthTimestampAnalyzer {

    public static void main(String[] args) {
        SparkSession spark = GetVMSpark.get("AuthTimestampAnalyzer");

        Dataset<Row> df = spark.read().option("header", "true").csv("hdfs://10.8.0.10:9000/team/team/bots_logins.csv");
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
    }
}
