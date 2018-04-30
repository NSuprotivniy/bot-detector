package Utils;

import nl.basjes.parse.useragent.UserAgent;
import nl.basjes.parse.useragent.UserAgentAnalyzer;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SparkSession;
import org.apache.spark.sql.api.java.UDF1;
import org.apache.spark.sql.types.DataTypes;

public class UserAgentParser {
    public static UserAgentAnalyzer uaa;

    public static void main(String[] args) {
        uaa = UserAgentAnalyzer
                .newBuilder()
                .hideMatcherLoadStats()
                .withCache(25000)
                .build();

        SparkSession spark = SparkSession.builder()
                .appName("UserAgentParser")
                .master("local[*]")
                .getOrCreate();
        System.out.println(args);
        Dataset<Row> df = spark.read().parquet(args[0]);

        UDF1 parseUserAgent = new UDF1<String, String>() {
            public String call(final String userAgentString) throws Exception {
                UserAgent agent = uaa.parse(userAgentString);
                StringBuilder stringBuilder = new StringBuilder();
                for (String fieldName: agent.getAvailableFieldNamesSorted()) {
                    stringBuilder.append(agent.getValue(fieldName));
                    stringBuilder.append(";:;");
                }
                String result = stringBuilder.toString();
                return result.substring(0, result.length() - 3);
            }
        };

        spark.udf().register("parseUserAgent", parseUserAgent, DataTypes.StringType);
        df.show(1, false);
        df = df.selectExpr("browserId", "from", "method", "operation", "referrer", "requestType", "timestamp", "to", "url", "parseUserAgent(userAgent) as userAgent", "userId", "hour");
        df.selectExpr("browserId", "from", "method", "operation", "referrer", "requestType", "timestamp", "to", "url", "split(userAgent, ';:;')[0] as DeviceClass",
                "split(userAgent, ';:;')[1] as DeviceName",
                "split(userAgent, ';:;')[2] as DeviceBrand",
                "split(userAgent, ';:;')[3] as DeviceCpu",
                "split(userAgent, ';:;')[4] as DeviceCpuBits",
                "split(userAgent, ';:;')[5] as OperatingSystemClass",
                "split(userAgent, ';:;')[6] as OperatingSystemName",
                "split(userAgent, ';:;')[7] as OperatingSystemVersion",
                "split(userAgent, ';:;')[8] as OperatingSystemNameVersion",
                "split(userAgent, ';:;')[9] as OperatingSystemVersionBuild",
                "split(userAgent, ';:;')[10] as LayoutEngineClass",
                "split(userAgent, ';:;')[11] as LayoutEngineName",
                "split(userAgent, ';:;')[12] as LayoutEngineVersion",
                "split(userAgent, ';:;')[13] as LayoutEngineVersionMajor",
                "split(userAgent, ';:;')[14] as LayoutEngineNameVersion",
                "split(userAgent, ';:;')[15] as LayoutEngineNameVersionMajor",
                "split(userAgent, ';:;')[16] as AgentClass",
                "split(userAgent, ';:;')[17] as AgentName",
                "split(userAgent, ';:;')[18] as AgentVersion",
                "split(userAgent, ';:;')[19] as AgentVersionMajor",
                "split(userAgent, ';:;')[20] as AgentNameVersion",
                "split(userAgent, ';:;')[21] as AgentNameVersionMajor",
                "userId", "hour").write().format("parquet").save("parsedUserAgent.parquet");
    }
}
