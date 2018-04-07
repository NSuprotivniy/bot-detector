package Helpers;

import org.apache.spark.sql.SparkSession;
import java.util.Map;

public class GetVMSpark {
    public static SparkSession get(String appName) {
        String VMSparkSessionConfig = "../config/VMSparkSession.conf";
        Map<String, String> config = ConfigReader.read(VMSparkSessionConfig);
        SparkSession spark = SparkSession
                .builder()
                .appName(appName)
                .master(config.get("master"))
                .config("spark.driver.host", config.get("spark.driver.host"))
                .config("spark.driver.port", config.get("spark.driver.port"))
                .config("spark.blockManager.port", config.get("spark.blockManager.port"))
                .getOrCreate();
        return spark;
    }
}
