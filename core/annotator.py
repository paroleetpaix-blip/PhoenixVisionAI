import cv2


class Annotator:

    def draw_detection(self, frame, detection):

        x1, y1, x2, y2 = detection.bbox

        label = (
            f"{detection.label} "
            f"{detection.confidence:.2f}"
        )

        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            label,
            (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2
        )

        return frame