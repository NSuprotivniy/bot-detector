package Helpers;

import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SparkSession;
import org.apache.spark.sql.types.DataTypes;
import java.text.SimpleDateFormat;



public class ParquetToCSV {

    private static String in_parquet = "../data/usersLogins.parquet";
    private static String out_csv = "../data/usersLogins.csv";
    private static int limit = 1_000_000;

    public static void main(String[] args) {

        if (args.length == 2)
        {
            in_parquet = args[0];
            out_csv = args[1];
            limit = Integer.parseInt(args[2]);
        }
    }

    public void parquetToCSV(String in_parquet, String out_csv, int limit) {
        SparkSession spark = SparkSession
                .builder()
                .appName("parquet to csv")
                .master("local[*]")
                .getOrCreate();

        Dataset<Row> users = spark.read().parquet(in_parquet);
        users.limit(limit).repartition(1).write().option("header", "true").csv(out_csv);
    }
}
