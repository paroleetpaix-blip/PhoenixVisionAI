from cloud.inference import CloudInference

cloud = CloudInference()

detections = cloud.predict(
    "frames/frame_000000.jpg"
)

print(detections)