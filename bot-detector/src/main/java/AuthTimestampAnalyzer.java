import Utils.GenerateData;
import org.apache.spark.ml.Pipeline;
import org.apache.spark.ml.PipelineModel;
import org.apache.spark.ml.PipelineStage;
import org.apache.spark.ml.classification.DecisionTreeClassificationModel;
import org.apache.spark.ml.classification.DecisionTreeClassifier;
import org.apache.spark.ml.evaluation.MulticlassClassificationEvaluator;
import org.apache.spark.ml.feature.*;
import org.apache.spark.sql.*;
import org.apache.spark.sql.types.DataTypes;
import org.apache.spark.sql.types.Metadata;
import org.apache.spark.sql.types.StructField;
import org.apache.spark.sql.types.StructType;
import static org.apache.spark.sql.functions.*;


public class AuthTimestampAnalyzer {

    /**
     *  Достает фичи из колонки "TIMESTAMP".
     *  Фичи: кол-во действий за разные промежутки времени
     *  (за все время, т.е. неделю, а также за пол дня. В итоге получится 15 фич)
     *  COUNT_ACT_WEEK - колонка с числом действий за неделю
     *  COUNT_ACT_1 - колонка с числом действий за первые пол дня
     *  ...
     */
    public static Dataset<Row> extractFeatures(Dataset<Row> df) {

        df = df.withColumn("ACT_1",
                when(col("TIMESTAMP").lt(GenerateData.FIRST_DAY_7PM_IN_SECONDS - 7 * 3600), col("TIMESTAMP")))
                .withColumn("ACT_2",
                        when(col("TIMESTAMP").gt(GenerateData.FIRST_DAY_7PM_IN_SECONDS - 7 * 3600)
                                        .and(col("TIMESTAMP").lt(GenerateData.FIRST_DAY_7PM_IN_SECONDS + 5 * 3600)),
                                col("TIMESTAMP")))
                .withColumn("ACT_3",
                        when(col("TIMESTAMP").gt(GenerateData.FIRST_DAY_7PM_IN_SECONDS + 5 * 3600)
                                        .and(col("TIMESTAMP").lt(GenerateData.SECOND_DAY_7PM_IN_SECONDS - 7 * 3600)),
                                col("TIMESTAMP")))
                .withColumn("ACT_4",
                        when(col("TIMESTAMP").gt(GenerateData.SECOND_DAY_7PM_IN_SECONDS - 7 * 3600).
                                        and(col("TIMESTAMP").lt(GenerateData.SECOND_DAY_7PM_IN_SECONDS + 5 * 3600)),
                                col("TIMESTAMP")))
                .withColumn("ACT_5",
                        when(col("TIMESTAMP").gt(GenerateData.SECOND_DAY_7PM_IN_SECONDS + 5 * 3600)
                                        .and(col("TIMESTAMP").lt(GenerateData.THIRD_DAY_7PM_IN_SECONDS - 5 * 3600)),
                                col("TIMESTAMP")))
                .withColumn("ACT_6",
                        when(col("TIMESTAMP").gt(GenerateData.THIRD_DAY_7PM_IN_SECONDS - 7 * 3600)
                                        .and(col("TIMESTAMP").lt(GenerateData.THIRD_DAY_7PM_IN_SECONDS + 5 * 3600)),
                                col("TIMESTAMP")));
        // ...

        df = df.groupBy("IP")
                .agg(count("TIMESTAMP").as("COUNT_ACT_WEEK"),
                        count("ACT_1").as("COUNT_ACT_1"),
                        count("ACT_2").as("COUNT_ACT_2"),
                        count("ACT_3").as("COUNT_ACT_3"),
                        count("ACT_4").as("COUNT_ACT_4"),
                        count("ACT_5").as("COUNT_ACT_5"),
                        count("ACT_6").as("COUNT_ACT_6"),
                        // ...
                        first("BOT_OR_HUMAN").as("label"));

        return df;
    }

    public static void main(String[] args) {
        SparkSession spark = SparkSession
                .builder()
                .appName("Java Spark count users activity")
                .master("local[4]")
                .getOrCreate();

        StructType schema = new StructType(new StructField[]{
                new StructField("IP", DataTypes.LongType, false, Metadata.empty()),
                new StructField("TIMESTAMP", DataTypes.LongType, false, Metadata.empty()),
                new StructField("BOT_OR_HUMAN", DataTypes.StringType, false, Metadata.empty())
        });

        Dataset<Row> data = spark.read().option("header", "true")
                .schema(schema)
                .csv("./res/generated_data.csv");

        data = extractFeatures(data).sort("IP");

        VectorAssembler assembler = new VectorAssembler()
                .setInputCols(new String[]{"COUNT_ACT_WEEK", "COUNT_ACT_1", "COUNT_ACT_2", "COUNT_ACT_3",
                        "COUNT_ACT_4", "COUNT_ACT_5", "COUNT_ACT_6"})
                .setOutputCol("features");

        data = assembler.transform(data);

        // Index labels, adding metadata to the label column.
        // Fit on whole dataset to include all labels in index.
        StringIndexerModel labelIndexer = new StringIndexer()
                .setInputCol("label")
                .setOutputCol("indexedLabel")
                .fit(data);

        // Automatically identify categorical features, and index them.
        VectorIndexerModel featureIndexer = new VectorIndexer()
                .setInputCol("features")
                .setOutputCol("indexedFeatures")
                .setMaxCategories(4) // features with > 4 distinct values are treated as continuous.
                .fit(data);

        Dataset<Row>[] splits = data.randomSplit(new double[]{0.7, 0.3});
        Dataset<Row> trainingData = splits[0];
        Dataset<Row> testData = splits[1];

        // Train a DecisionTree model.
        DecisionTreeClassifier dt = new DecisionTreeClassifier()
                .setLabelCol("indexedLabel")
                .setFeaturesCol("indexedFeatures");

        // Convert indexed labels back to original labels.
        IndexToString labelConverter = new IndexToString()
                .setInputCol("prediction")
                .setOutputCol("predictedLabel")
                .setLabels(labelIndexer.labels());

        // Chain indexers and tree in a Pipeline.
        Pipeline pipeline = new Pipeline()
                .setStages(new PipelineStage[]{labelIndexer, featureIndexer, dt, labelConverter});

        // Train model. This also runs the indexers.
        PipelineModel model = pipeline.fit(trainingData);

        // Make predictions.
        Dataset<Row> predictions = model.transform(testData);

        // Select example rows to display.
        predictions.select("predictedLabel", "label", "features").show(5, false);

        // Select (prediction, true label) and compute test error.
        MulticlassClassificationEvaluator evaluator = new MulticlassClassificationEvaluator()
                .setLabelCol("indexedLabel")
                .setPredictionCol("prediction")
                .setMetricName("accuracy");
        double accuracy = evaluator.evaluate(predictions);
        System.out.println("Test Error = " + (1.0 - accuracy));

        DecisionTreeClassificationModel treeModel =
                (DecisionTreeClassificationModel) (model.stages()[2]);
        System.out.println("Learned classification tree model:\n" + treeModel.toDebugString());

        spark.stop();
    }
}