from pyspark.sql import SparkSession
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType
import os
# import time

# Initialize SparkSession
spark = SparkSession.builder \
    .appName("FrameAnnotationStreamProcessor") \
    .config("spark.sql.streaming.schemaInference", "true") \
    .getOrCreate()

# Suppress excessive INFO logging from Spark itself
spark.sparkContext.setLogLevel("WARN")

frames_input_path = "/app/frames"
checkpoint_location = "/opt/app/checkpoints/annotations_checkpoint"


def annotate_frame(image_path_string):
    # time.sleep(0.05) # Keep this commented for initial testing unless needed
    frame_id = os.path.basename(image_path_string)
    annotation = f"Stream Annotation for {frame_id}: type='detection', count=10"
    print(f"Processing stream frame: {frame_id}")
    return annotation


annotate_frame_udf = udf(annotate_frame, StringType())

df_stream = spark.readStream \
    .format("binaryFile") \
    .option("recursiveFileLookup", "true") \
    .option("pathGlobFilter", "*.jpg") \
    .option("maxFilesPerTrigger", 5) \
    .load(frames_input_path)

annotated_stream_df = df_stream.withColumn(
    "annotation", annotate_frame_udf(df_stream["path"]))


annotation_only_df = annotated_stream_df.select("annotation")
query = annotation_only_df.writeStream \
    .outputMode("append") \
    .format("console") \
    .option("truncate", "false") \
    .option("numRows", 1)  \
    .start()

print(
    f"Spark Streaming job started. Monitoring {frames_input_path} for new frames.")
print("Console sink is configured to show only the 'annotation' column.")
print("Check Spark UI (http://localhost:4040 if running locally) for detailed progress.")

query.awaitTermination()
