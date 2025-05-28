from pyspark.sql import SparkSession
import os
import cv2
import numpy as np
from ultralytics import YOLO


spark = SparkSession.builder \
    .appName("ImageAnnotationBatchProcessor") \
    .config("spark.sql.streaming.schemaInference", "true") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

frames_input_path = "/app/frames"
checkpoint_location = "/app/frames/checkpoints"


model = YOLO("yolov8n.pt")


def process_batch(df, epoch_id):

    imgs, paths = get_images_and_paths(df)
    results = model(imgs)

    for path, img, result in zip(paths, imgs, results):
        for box in result.boxes:
            label = model.names[int(box.cls[0])]
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(img, label, (x1, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        base_dir = os.path.basename(os.path.dirname(path))
        filename = os.path.basename(path)
        annotated_path = os.path.join(
            frames_input_path, base_dir, "annotated", filename)
        os.makedirs(os.path.dirname(annotated_path), exist_ok=True)
        cv2.imwrite(annotated_path, img)
        print(f"[INFO] {filename}: {len(result.boxes)} objects detected")


def get_images_and_paths(df):
    imgs, paths = [], []
    for row in df.select("path", "content").collect():
        path = row.path.replace("file:", "")
        img_array = np.frombuffer(row.content, dtype=np.uint8)
        imgs.append(cv2.imdecode(img_array, cv2.IMREAD_COLOR))
        paths.append(path)
    return imgs, paths


df_stream = spark.readStream \
    .format("binaryFile") \
    .option("recursiveFileLookup", "true") \
    .option("pathGlobFilter", "*.jpg") \
    .option("maxFilesPerTrigger", 64) \
    .option("includeFileContent", "true") \
    .load(frames_input_path)


query = df_stream.writeStream \
    .foreachBatch(process_batch) \
    .option("checkpointLocation", checkpoint_location) \
    .start()


print(f"[INFO] Spark Streaming job started. Watching {frames_input_path}")
print("Check Spark UI (http://localhost:4040) for job progress.")
query.awaitTermination()
