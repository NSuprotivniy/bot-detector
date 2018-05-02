package Utils;

import nl.basjes.parse.useragent.UserAgent;
import nl.basjes.parse.useragent.UserAgentAnalyzer;
import org.apache.spark.SparkContext;
import org.apache.spark.broadcast.Broadcast;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SparkSession;
import org.apache.spark.sql.api.java.UDF1;
import org.apache.spark.sql.types.DataTypes;

public class UserAgentParser {
    public static void main(String[] args) {
        if (args.length < 2) {
            System.err.println("arguments: <path_to_input_parquet> <<path_to_output_parquet>>");
            return;
        }

        String inParquet = args[0];
        String outParquet = args[1];

        UserAgentAnalyzer uaa = UserAgentAnalyzer
                .newBuilder()
                .hideMatcherLoadStats()
                .withCache(25000)
                .build();

        SparkSession spark = SparkSession.builder()
                .appName("UserAgentParser")
                .master("local[*]")
                .getOrCreate();

        SparkContext sparkContext = spark.sparkContext();
        Broadcast<UserAgentAnalyzer> uaaBroadcast = sparkContext.broadcast(uaa, scala.reflect.ClassManifestFactory.fromClass(UserAgentAnalyzer.class));

        Dataset<Row> df = spark.read().parquet(inParquet);
        int partitions = df.rdd().getNumPartitions();
        df.printSchema();
        System.out.println("Count: " + df.count());

        UDF1 parseUserAgent = new UDF1<String, String>() {
            public String call(final String userAgentString) throws Exception {
                UserAgentAnalyzer uaa = uaaBroadcast.getValue();
                StringBuilder stringBuilder = new StringBuilder();
                UserAgent agent = uaa.parse(userAgentString);
                for (String fieldName: agent.getAvailableFieldNamesSorted()) {
                    stringBuilder.append(agent.getValue(fieldName));
                    stringBuilder.append(";:;");
                }
                String result = stringBuilder.toString();
                return result.substring(0, result.length() - 3);
            }
        };

        spark.udf().register("parseUserAgent", parseUserAgent, DataTypes.StringType);

        df = df.selectExpr("*", "parseUserAgent(userAgent) as parsedUserAgent")
                .selectExpr("*",
                    "split(parsedUserAgent, ';:;')[0] as DeviceClass",
                    "split(parsedUserAgent, ';:;')[1] as DeviceName",
                    "split(parsedUserAgent, ';:;')[2] as DeviceBrand",
                    "split(parsedUserAgent, ';:;')[3] as DeviceCpu",
                    "split(parsedUserAgent, ';:;')[4] as DeviceCpuBits",
                    "split(parsedUserAgent, ';:;')[5] as OperatingSystemClass",
                    "split(parsedUserAgent, ';:;')[6] as OperatingSystemName",
                    "split(parsedUserAgent, ';:;')[7] as OperatingSystemVersion",
                    "split(parsedUserAgent, ';:;')[8] as OperatingSystemNameVersion",
                    "split(parsedUserAgent, ';:;')[9] as OperatingSystemVersionBuild",
                    "split(parsedUserAgent, ';:;')[10] as LayoutEngineClass",
                    "split(parsedUserAgent, ';:;')[11] as LayoutEngineName",
                    "split(parsedUserAgent, ';:;')[12] as LayoutEngineVersion",
                    "split(parsedUserAgent, ';:;')[13] as LayoutEngineVersionMajor",
                    "split(parsedUserAgent, ';:;')[14] as LayoutEngineNameVersion",
                    "split(parsedUserAgent, ';:;')[15] as LayoutEngineNameVersionMajor",
                    "split(parsedUserAgent, ';:;')[16] as AgentClass",
                    "split(parsedUserAgent, ';:;')[17] as AgentName",
                    "split(parsedUserAgent, ';:;')[18] as AgentVersion",
                    "split(parsedUserAgent, ';:;')[19] as AgentVersionMajor",
                    "split(parsedUserAgent, ';:;')[20] as AgentNameVersion",
                    "split(parsedUserAgent, ';:;')[21] as AgentNameVersionMajor")
                .drop("parsedUserAgent");

        df.repartition(partitions).write().mode("overwrite").format("parquet").save(outParquet);
    }
}
