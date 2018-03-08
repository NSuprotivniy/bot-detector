package Utils;

import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SparkSession;
import org.apache.spark.sql.types.DataTypes;
import static org.apache.spark.sql.functions.*; //max, min
import static org.apache.spark.sql.functions.col;

public class TimeUnitsCounter {

    //datadiff()
    public static double countTimeIntervalOfAllDataInDays(SparkSession spark, Dataset<Row> df, boolean mils) {
        return (Double) df.withColumn("TIMESTAMP", col("TIMESTAMP").cast(DataTypes.LongType))
                .select(col("TIMESTAMP"))
                .agg(max("TIMESTAMP").alias("MAX"), min("TIMESTAMP").alias("MIN"))
                .withColumn("EXPLORED_TIME_INTERVAL", col("MAX").minus(col("MIN")))
                .select(col("EXPLORED_TIME_INTERVAL"))
                .withColumn("EXPLORED_TIME_INTERVAL", col("EXPLORED_TIME_INTERVAL").divide(60 * 60 * 24 * (mils ? 1000 : 1)))
                .toJavaRDD().collect().get(0).get(0);
    }
}
