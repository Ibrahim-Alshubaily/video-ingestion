from pyspark.sql import SparkSession
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType
import os
import cv2
import numpy as np
from ultralytics import YOLO


# Initialize SparkSession
spark = SparkSession.builder \
    .appName("FrameAnnotationStreamProcessor") \
    .config("spark.sql.streaming.schemaInference", "true") \
    .getOrCreate()

# Suppress excessive INFO logging
spark.sparkContext.setLogLevel("WARN")

frames_input_path = "/app/frames"
output_path_base = "/app/frames/annotated"
checkpoint_location = "/app/frames/checkpoints"


def annotate_frame(image_path_string):
    if not hasattr(annotate_frame, "model"):
        annotate_frame.model = YOLO("yolov8n.pt")

    model = annotate_frame.model

    if image_path_string.startswith("file:/"):
        image_path_string = image_path_string.replace("file:", "")

    frame_id = os.path.basename(image_path_string)
    img = cv2.imread(image_path_string)
    if img is None:
        return f"Error: cannot load {frame_id}"

    results = model(img)
    object_count = 0

    for result in results:
        for box in result.boxes:
            label = model.names[int(box.cls[0])]
            object_count += 1
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(img, label, (x1, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    annotated_path = image_path_string.replace(
        frames_input_path, output_path_base)
    os.makedirs(os.path.dirname(annotated_path), exist_ok=True)
    cv2.imwrite(annotated_path, img)
    return f"{frame_id}: {object_count} vehicles detected"


annotate_frame_udf = udf(annotate_frame, StringType())

df_stream = spark.readStream \
    .format("binaryFile") \
    .option("recursiveFileLookup", "true") \
    .option("pathGlobFilter", "*.jpg") \
    .option("maxFilesPerTrigger", 5) \
    .load(frames_input_path)

# Add annotation column
annotated_stream_df = df_stream.withColumn(
    "annotation", annotate_frame_udf(df_stream["path"])
)

# Show annotations only in console
annotation_only_df = annotated_stream_df.select("annotation")
query = annotation_only_df.writeStream \
    .outputMode("append") \
    .format("console") \
    .option("truncate", "false") \
    .option("numRows", 1) \
    .option("checkpointLocation", checkpoint_location) \
    .start()

print(
    f"Spark Streaming job started. Monitoring {frames_input_path} for new frames.")
print("Console sink will display the annotation summaries.")
print("Check Spark UI (http://localhost:4040) for job progress.")

query.awaitTermination()
